from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
import pendulum # pour gérer les dates en python
import datetime
import praw  # Librairie pour interagir avec l'API de Reddit
import psycopg2 # pour se connecter à PostgreSQL et insérer des données dans la base de données.
from psycopg2.extras import Json
import pandas as pd
import re #Utilisé pour les expressions régulières (nettoyage des textes).
from airflow.models import Variable

# Paramètres de configuration
DB_HOST = "postgres"
DB_PORT = "5432"

# Liste des secteurs à traiter
sectors = ["inwi", "InternetMaroc"]

# Fonction d'extraction des données pour un secteur donné
def fetch_posts_with_comments(ti, sector_name):
    reddit = praw.Reddit(
        client_id=Variable.get("REDDIT_CLIENT_ID"),
        client_secret=Variable.get("REDDIT_CLIENT_SECRET"),
        user_agent=Variable.get("REDDIT_USER_AGENT")
    )
    
    # Extraction des données de posts et commentaires pour le secteur
    posts_data = []
    for submission in reddit.subreddit("all").search(sector_name, sort="hot", limit=50):
        post_info = {
            'post_id': submission.id,
            'post_title': submission.title,
            'post_text': submission.selftext,
            'post_date': datetime.datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
            'nbr_likes': submission.score,
            'nbr_reposts': submission.num_crossposts,
            'nbr_characters': len(submission.selftext),
            'author_id': submission.author.name if submission.author else "N/A",
            'comments': [
                {
                    'comment_order': i + 1,
                    'comment_date': datetime.datetime.utcfromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                    'comment_text': comment.body,
                    'comment_likes': comment.score
                } for i, comment in enumerate(submission.comments.list())
            ]
        }
        posts_data.append(post_info)

    # Push des données dans XCom pour être utilisées dans les tâches suivantes
    ti.xcom_push(key=f'{sector_name}_data', value=posts_data)

# Fonction de traitement des données de commentaires pour un secteur donné
def process_data(ti, sector_name):
    reddit_data = ti.xcom_pull(key=f'{sector_name}_data')
    
    if not reddit_data:
        print(f"Aucune donnée n'a été récupérée pour le secteur {sector_name}.")
        return

    # Extraire uniquement les commentaires
    comments_data = [comment for post in reddit_data if 'comments' in post for comment in post['comments']]
    
    if not comments_data:
        print(f"Aucun commentaire trouvé pour le secteur {sector_name}.")
        return

    comments_df = pd.DataFrame(comments_data)

    # Nettoyer le texte des commentaires
    def clean_text(text):
        text = re.sub(r'@[A-Za-z0-9]+', '', text)
        text = re.sub(r'#', '', text)
        text = re.sub(r'RT[\s]+', '', text)
        text = re.sub(r'https?:\/\/\S+', '', text)
        text = re.sub(r':', '', text)
        return text

    def remove_emoji(string):
        emoji_pattern = re.compile(
            "["  
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F6FF"
            u"\U0001F1E0-\U0001F1FF"
            u"\u2640-\u2642"
            u"\u2600-\u2B55"
            u"\u200d"
            u"\u23cf"
            u"\u23e9"
            u"\u231a"
            u"\ufe0f"
            u"\u3030"
            "]+", 
            flags=re.UNICODE
        )
        return emoji_pattern.sub(r'', string)

    comments_df['cleaned_comment_text'] = comments_df['comment_text'].apply(
        lambda text: remove_emoji(clean_text(text)) if isinstance(text, str) else ""
    )

    # Sauvegarde temporaire pour chaque secteur
    output_path = f'/opt/airflow/dags/cleaned_comments_{sector_name}.csv'
    comments_df.to_csv(output_path, index=False)
    print(f"Commentaires nettoyés pour {sector_name} sauvegardés dans {output_path}")

    # Pousse les données nettoyées dans XCom
    ti.xcom_push(key=f'cleaned_comments_{sector_name}', value=comments_df.to_dict(orient='records'))

# Fonction d'insertion des données pour un secteur donné
def insert_data_to_postgresql(ti, sector_name):
    cleaned_comments = ti.xcom_pull(key=f'cleaned_comments_{sector_name}')
    df = pd.DataFrame(cleaned_comments)
    
    try:
        with psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname="airflow", user="airflow", password="airflow"
        ) as conn:
            with conn.cursor() as cur:
                for _, row in df.iterrows():
                    post_data = (
                        row['post_id'],
                        row['post_title'],
                        row['post_text'],
                        datetime.datetime.strptime(row['post_date'], '%Y-%m-%d %H:%M:%S'),
                        row['nbr_likes'],
                        row['nbr_reposts'],
                        row['nbr_characters'],
                        row['author_id'],
                        Json(row['comments'])
                    )
                    cur.execute(f"""
                    INSERT INTO reddit_posts_{sector_name} (post_id, post_title, post_text, post_date,
                                                    nbr_likes, nbr_reposts, nbr_characters, author_id, comments)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (post_id) DO NOTHING;
                    """, post_data)
                conn.commit()
    except Exception as e:
        print(f"Erreur lors de l'insertion des données pour {sector_name} : {e}")

# Définition du DAG unique pour plusieurs secteurs
with DAG(
    'etl_pipeline_multiple_sectors',  #Nom du DAG
    default_args={ # Arguments par défaut pour les tâches du DAG
        'owner': 'airflow',  # Propriétaire de ce DAG
        'depends_on_past': False, # Les tâches ne dépendent pas des exécutions passées
        'email_on_failure': False,
        'retries': 4,
        'start_date': pendulum.today('UTC').add(days=-2),
    },
    description='ETL pipeline to fetch, process, and insert Reddit posts for multiple sectors into PostgreSQL',
    schedule_interval=None,
    tags=['reddit', 'etl', 'multiple_sectors'],
) as dag:

    for sector in sectors:
        extract_data = PythonOperator(
            task_id=f'extract_data_{sector}',
            python_callable=fetch_posts_with_comments,
            op_kwargs={'sector_name': sector}
        )
        
        create_table = SQLExecuteQueryOperator(
            task_id=f'create_table_{sector}',
            conn_id='postgres_default',
            sql=f"""
                CREATE TABLE IF NOT EXISTS reddit_posts_{sector} (
                    post_id VARCHAR PRIMARY KEY,
                    post_title TEXT,
                    post_text TEXT,
                    post_date TIMESTAMP,
                    nbr_likes INTEGER,
                    nbr_reposts INTEGER,
                    nbr_characters INTEGER,
                    author_id VARCHAR,
                    comments JSONB
                );
            """,
            hook_params={'schema': 'airflow'}
        )
        
        process_comments = PythonOperator(
            task_id=f'process_data_{sector}',
            python_callable=process_data,
            op_kwargs={'sector_name': sector}
        )
        
        insert_data = PythonOperator(
            task_id=f'insert_data_{sector}',
            python_callable=insert_data_to_postgresql,
            op_kwargs={'sector_name': sector}
        )
        
        # Ordre des tâches
        extract_data >> create_table >> process_comments >> insert_data
