# imdb_thread_grabber

Purpose built to grab a Blade Runner thread before IMDB yanks the forum feature, [as requested here](https://www.reddit.com/r/scifi/comments/5s0iiv/imdb_message_boards_being_removed_long_running/).

YMMV.

## Usage

A little janky.  Sorry.

From the repo root:

    python -m grabber <url to forum thread> -j -o <path/to/output_dir>
    
For example:

    python -m grabber http://www.imdb.com/title/tt0083658/board/thread/117969472 -j -o ~/Desktop/imdb_output/
    
Again: YMMV.  Not tested anywhere but OS X.  Mobile links *should* work.
