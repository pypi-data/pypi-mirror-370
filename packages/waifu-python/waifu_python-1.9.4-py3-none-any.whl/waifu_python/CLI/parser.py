import argparse

def create_parser():
    parser = argparse.ArgumentParser(
        prog='waifu-python',
        description='Waifu-Python API client',
    )
    
    parser._positionals.title = "Required Arguments"
    
    parser.add_argument('api', nargs='?', help='API name')
    parser.add_argument('query', nargs='?', help='Search query (tag) if any')
    
    parser.add_argument('--limit', type=int, default=1, help='Number of images to retrieve')
    
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--nsfw', action='store_true', help='Fetch in NSFW mode')
    mode_group.add_argument('--sfw', action='store_true', help='Fetch in SFW mode')
    
    parser.add_argument('--tags', action='store_true', help='Retrieve available tags for the specified API')
    
    parser.add_argument('--list', action='store_true', help='List all available API names with SFW/NSFW availability')
    
    parser.add_argument('--login', action='store_true', help='Login to Pixiv and retrieve auth tokens')
    parser.add_argument('--refresh', type=str, help='Refresh Pixiv token; provide old refresh token')

    return parser

if __name__ == "__main__":
    parser = create_parser()
    parser.print_help()
