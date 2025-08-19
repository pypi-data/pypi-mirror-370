import os
import time
import json
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from openwrite.utils.valkey_client import valkey_client
from openwrite.utils.models import View, Like
from openwrite.utils.db import init_engine, SessionLocal
from openwrite.utils.helpers import send_activity
from datetime import datetime, timezone

load_dotenv()

VALKEY_INTERVAL = int(os.getenv('VALKEY_INTERVAL', 5))

def get_db_session():
    db_type = os.getenv('DB_TYPE', 'sqlite')
    db_path = os.getenv('DB_PATH', 'sqlite:///db.sqlite')
    
    if db_type == "sqlite":
        engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    elif db_type == "mysql":
        engine = create_engine(db_path)
    else:
        raise ValueError("Unsupported DB_TYPE. Use 'sqlite' or 'mysql'.")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def process_views():
    db = get_db_session()
    try:
        queued_views = valkey_client.client.lrange('openwrite:views:queue', 0, -1)
        
        for view_data in reversed(queued_views):
            view_json = json.loads(view_data)
            blog_id = view_json['blog_id']
            post_id = view_json['post_id']
            ip_hash = view_json['ip_hash']
            timestamp = datetime.fromisoformat(view_json['timestamp'])
            
            existing_view = db.query(View).filter_by(
                blog=blog_id,
                post=post_id,
                hash=ip_hash
            ).first()
            
            if not existing_view:
                new_view = View(
                    blog=blog_id,
                    post=post_id,
                    hash=ip_hash,
                    date=timestamp
                )
                db.add(new_view)
        
        db.commit()
        
        valkey_client.client.ltrim('openwrite:views:queue', len(queued_views), -1)
    
    finally:
        db.close()

def process_likes():
    db = get_db_session()
    try:
        queued_likes = valkey_client.client.lrange('openwrite:likes:queue', 0, -1)
        
        for like_data in reversed(queued_likes):
            like_json = json.loads(like_data)
            blog_id = like_json['blog_id']
            post_id = like_json['post_id']
            ip_hash = like_json['ip_hash']
            action = like_json['action']
            timestamp = datetime.fromisoformat(like_json['timestamp'])
            
            existing_like = db.query(Like).filter_by(
                blog=blog_id,
                post=post_id,
                hash=ip_hash
            ).first()
            
            if action == 'add' and not existing_like:
                new_like = Like(
                    blog=blog_id,
                    post=post_id,
                    hash=ip_hash,
                    date=timestamp
                )
                db.add(new_like)
            elif action == 'remove' and existing_like:
                db.delete(existing_like)
        
        db.commit()
        
        valkey_client.client.ltrim('openwrite:likes:queue', len(queued_likes), -1)
    
    finally:
        db.close()

def process_federation_activities():
    queued_activities = valkey_client.get_queued_federation_activities()
    
    for activity_data in queued_activities:
        data = json.loads(activity_data)
        activity = data['activity']
        blog_id = data['blog_id']
        priv_key = data['priv_key']
        blog_url = data['blog_url']
        inbox_url = data['inbox_url']
        
        try:
            send_activity(activity, priv_key, blog_url, inbox_url)
        except Exception as e:
            print(f"Error sending federation activity: {e}")
    
    valkey_client.remove_federation_activities(len(queued_activities))

def main():
    db_type = os.getenv('DB_TYPE', 'sqlite')
    db_path = os.getenv('DB_PATH', 'sqlite:///db.sqlite')
    init_engine(db_type, db_path)

    while True:
        print(f"Processing views, likes, and federation activities at {datetime.now()}")
        process_views()
        process_likes()
        process_federation_activities()
        time.sleep(VALKEY_INTERVAL * 60)

if __name__ == "__main__":
    main()