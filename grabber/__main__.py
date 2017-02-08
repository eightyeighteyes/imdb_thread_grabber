import argparse
import json
import os

from grabber import Grabber


def get_args():
    parser = argparse.ArgumentParser(description="Archives an IMDB thread from a given url.")
    parser.add_argument('url', type=str, help="Thread URL (eg, http://www.imdb.com/title"
                                              "/tt0083658/board/thread/117969472)")

    parser.add_argument('-j', '--json', action='store_true', default=False,
                        help="Enables json output.")
    parser.add_argument('-w', '--html', action='store_true', default=False,
                        help="Enables web output.")
    parser.add_argument('-o', '--output', type=str, default='',
                        help="Path for archive output.")

    return parser.parse_args()


def check_args(args):
    if args.json or args.html:
        if not args.output:
            raise RuntimeError("Output path (-o) required for output.")
        output_path = os.path.expanduser(args.output)
        if not os.path.exists(output_path) or not os.path.isdir(output_path):
            raise OSError("Output path must be a directory that exists.")

        if not args.url.startswith('http'):
            raise RuntimeError("URL must be a valid URL.")
        if 'imdb.com' not in args.url:
            raise RuntimeError("URL must be for IMDB.")
        if 'board/' not in args.url:
            raise RuntimeError("URL must be an IMDB forum thread.")


def run_grabber():
    args = get_args()
    check_args(args)
    url = args.url
    json_output = args.json
    html_output = args.html
    output_path = os.path.expanduser(args.output)

    grabber = Grabber(url)
    grabber.run()

    if json_output:
        with open(os.path.join(output_path, '{}.json'.format(grabber.title)), 'w') as output:
            json.dump(grabber.json_output, output, indent=2)

    if html_output:
        raise NotImplementedError("HTML output is not implemented yet.")


if __name__ == '__main__':
    run_grabber()
