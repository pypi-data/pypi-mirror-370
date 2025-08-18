class Cdn:
    def __init__(self):
        self.mapping = {
            "d-medusa-media": 'https://ik.imagekit.io/lyu8ar8mu/',
            "d-review-media": 'https://ik.imagekit.io/lyu8ar8mu/review-media/'
        }
        self.supported_extensions = ['jpg', 'jpeg', 'png', 'gif', 'svg', 'webp','avif']
    
    def get_edge_url(self, url: str, region: str = None):
        if url is None:
            return None
            
        if not isinstance(url, str):
            return url
        
        if url.lower().split('?')[0].split('.')[-1] not in self.supported_extensions:
            return url
        
        # Build exhaustive mapping using the provided region
        exhaustive_mapping = {}
        for key, value in self.mapping.items():
            if region:
                exhaustive_mapping[f"http://{key}.s3.{region}.amazonaws.com/"] = value
                exhaustive_mapping[f"https://{key}.s3.{region}.amazonaws.com/"] = value
            exhaustive_mapping[f"http://{key}.s3.amazonaws.com/"] = value
            exhaustive_mapping[f"https://{key}.s3.amazonaws.com/"] = value
        
        for key, value in exhaustive_mapping.items():
            if key in url:
                return url.replace(key, value)
                
        return url