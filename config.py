import os
from dotenv import load_dotenv
import sys

class Config:
    def __init__(self):
        # Try multiple ways to load environment variables
        self.load_environment()
        
        # Set configuration values
        self.AVIATIONSTACK_API_KEY = os.getenv('AVIATIONSTACK_API_KEY')
        self.OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
        self.SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-123')
        
        # Verify configuration
        self.verify()
    
    def load_environment(self):
        """Attempt to load environment variables from multiple sources"""
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        
        # Try loading with UTF-8 encoding first
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                load_dotenv(stream=f)
            return
        except UnicodeDecodeError:
            pass
        except Exception as e:
            print(f"Warning: Could not load .env file as UTF-8 - {str(e)}")
        
        # Try loading with system default encoding
        try:
            load_dotenv(env_path)
            return
        except Exception as e:
            print(f"Warning: Could not load .env file - {str(e)}")
        
        # Fallback to system environment variables
        print("Using system environment variables only")
    
    def verify(self):
        """Verify required configurations are present"""
        if not self.AVIATIONSTACK_API_KEY:
            print("Error: AVIATIONSTACK_API_KEY is missing from environment variables")
            sys.exit(1)
        if not self.OPENROUTER_API_KEY:
            print("Warning: OPENROUTER_API_KEY is missing - AI features will be disabled")

# Create config instance
config = Config()