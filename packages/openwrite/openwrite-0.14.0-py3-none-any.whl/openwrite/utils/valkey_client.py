import os
import redis
import json
from datetime import datetime, timezone

class ValkeyClient:
    def __init__(self):
        self.enabled = os.getenv('VALKEY_ENABLED', 'no').lower() == 'yes'
        self.client = None
        
        if self.enabled:
            self.client = redis.Redis(
                host=os.getenv('VALKEY_HOST', 'localhost'),
                port=int(os.getenv('VALKEY_PORT', 6379)),
                db=int(os.getenv('VALKEY_DB', 0)),
                password=os.getenv('VALKEY_PASSWORD', None),
                decode_responses=True
            )
    
    def is_enabled(self):
        return self.enabled and self.client is not None
    
    def queue_view(self, blog_id, post_id, ip_hash, user_agent):
        """Queue a view to be processed later"""
        if not self.is_enabled():
            return False
        
        view_data = {
            'blog_id': blog_id,
            'post_id': post_id,
            'ip_hash': ip_hash,
            'user_agent': user_agent,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        self.client.lpush('openwrite:views:queue', json.dumps(view_data))
        return True
    
    def queue_like(self, blog_id, post_id, ip_hash, action='add'):
        """Queue a like action to be processed later"""
        if not self.is_enabled():
            return False
        
        like_data = {
            'blog_id': blog_id,
            'post_id': post_id,
            'ip_hash': ip_hash,
            'action': action,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        self.client.lpush('openwrite:likes:queue', json.dumps(like_data))
        return True
    
    def check_queued_view(self, blog_id, post_id, ip_hash):
        """Check if there's a queued view for this user/post combination"""
        if not self.is_enabled():
            return False
        
        queue_items = self.client.lrange('openwrite:views:queue', 0, -1)
        for item in queue_items:
            try:
                data = json.loads(item)
                if (data['blog_id'] == blog_id and 
                    data['post_id'] == post_id and 
                    data['ip_hash'] == ip_hash):
                    return True
            except (json.JSONDecodeError, KeyError):
                continue
        return False
    
    def check_queued_like(self, blog_id, post_id, ip_hash):
        """Check if there's a queued like for this user/post combination"""
        if not self.is_enabled():
            return False
        
        queue_items = self.client.lrange('openwrite:likes:queue', 0, -1)
        net_likes = 0 
        
        for item in queue_items:
            try:
                data = json.loads(item)
                if (data['blog_id'] == blog_id and 
                    data['post_id'] == post_id and 
                    data['ip_hash'] == ip_hash):
                    if data['action'] == 'add':
                        net_likes += 1
                    elif data['action'] == 'remove':
                        net_likes -= 1
            except (json.JSONDecodeError, KeyError):
                continue
        
        return net_likes > 0
    
    def count_queued_views(self, blog_id, post_id):
        """Count queued views for a specific post"""
        if not self.is_enabled():
            return 0
        
        queue_items = self.client.lrange('openwrite:views:queue', 0, -1)
        count = 0
        
        for item in queue_items:
            try:
                data = json.loads(item)
                if data['blog_id'] == blog_id and data['post_id'] == post_id:
                    count += 1
            except (json.JSONDecodeError, KeyError):
                continue
        
        return count
    
    def count_queued_likes(self, blog_id, post_id):
        """Count net queued likes for a specific post"""
        if not self.is_enabled():
            return 0
        
        queue_items = self.client.lrange('openwrite:likes:queue', 0, -1)
        net_likes = 0
        
        for item in queue_items:
            try:
                data = json.loads(item)
                if data['blog_id'] == blog_id and data['post_id'] == post_id:
                    if data['action'] == 'add':
                        net_likes += 1
                    elif data['action'] == 'remove':
                        net_likes -= 1
            except (json.JSONDecodeError, KeyError):
                continue
        
        return net_likes

    def queue_federation_activity(self, activity, blog_id, priv_key, blog_url, inbox_url):
        if not self.is_enabled():
            return False
        
        activity_data = json.dumps({
            'activity': activity,
            'blog_id': blog_id,
            'priv_key': priv_key,
            'blog_url': blog_url,
            'inbox_url': inbox_url
        })
        
        return self.client.rpush('openwrite:federation:queue', activity_data)


    def get_queued_federation_activities(self):
        if not self.is_enabled():
            return []
        
        return self.client.lrange('openwrite:federation:queue', 0, -1)

    def remove_federation_activities(self, count):
        if not self.is_enabled():
            return
        
        self.client.ltrim('openwrite:federation:queue', count, -1)

valkey_client = ValkeyClient()