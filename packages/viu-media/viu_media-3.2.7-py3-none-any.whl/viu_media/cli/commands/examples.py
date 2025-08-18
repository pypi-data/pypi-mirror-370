download = """
\b
\b\bExamples:
  # Download all available episodes
  # multiple titles can be specified with -t option
  viu download -t <anime-title> -t <anime-title>
  # -- or --
  viu download -t <anime-title> -t <anime-title> -r ':'
\b
  # download latest episode for the two anime titles
  # the number can be any no of latest episodes but a minus sign
  # must be present
  viu download -t <anime-title> -t <anime-title> -r '-1'
\b
  # latest 5
  viu download -t <anime-title> -t <anime-title> -r '-5'
\b
  # Download specific episode range
  # be sure to observe the range Syntax
  viu download -t <anime-title> -r '<episodes-start>:<episodes-end>:<step>'
\b
  viu download -t <anime-title> -r '<episodes-start>:<episodes-end>'
\b
  viu download -t <anime-title> -r '<episodes-start>:'
\b
  viu download -t <anime-title> -r ':<episodes-end>'
\b
  # download specific episode
  # remember python indexing starts at 0
  viu download -t <anime-title> -r '<episode-1>:<episode>'
\b
  # merge subtitles with ffmpeg to mkv format; hianime tends to give subs as separate files
  # and dont prompt for anything
  # eg existing file in destination instead remove
  # and clean
  # ie remove original files (sub file and vid file)
  # only keep merged files
  viu download -t <anime-title> --merge --clean --no-prompt
\b
  # EOF is used since -t always expects a title
  # you can supply anime titles from file or -t at the same time
  # from stdin
  echo -e "<anime-title>\\n<anime-title>\\n<anime-title>" | viu download -t "EOF" -r <range> -f -
\b
  # from file
  viu download -t "EOF" -r <range> -f <file-path>
"""
search = """
\b
\b\bExamples:
  # basic form where you will still be prompted for the episode number
  # multiple titles can be specified with the -t option
  viu search -t <anime-title> -t <anime-title>
\b
  # binge all episodes with this command
  viu search -t <anime-title> -r ':'
\b
  # watch latest episode
  viu search -t <anime-title> -r '-1'
\b
  # binge a specific episode range with this command
  # be sure to observe the range Syntax
  viu search -t <anime-title> -r '<start>:<stop>'
\b
  viu search -t <anime-title> -r '<start>:<stop>:<step>'
\b
  viu search -t <anime-title> -r '<start>:'
\b
  viu search -t <anime-title> -r ':<end>'
"""
