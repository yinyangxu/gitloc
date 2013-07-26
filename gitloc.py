#!/usr/bin/env python


import os
import re
import sys
import datetime
from subprocess import Popen, PIPE


git_log_cmd = 'git log --pretty="%ad" --stat --no-merges --date=short'


def read_stdout(cmd):
    p = Popen(cmd, stdout=PIPE, stderr=PIPE,
              universal_newlines=True, shell=True)

    stdout, stderr = p.communicate()

    if p.returncode != 0:
        return

    return stdout


def is_commit_line(line):
    return re.search('\d{4}-\d{2}-\d{2}', line)


def is_count_line(line):
    return re.search('changed', line)


def count_loc(lines):
    # TODO: handle the case for projects over one year.

    week = None
    week_loc = {}  # {week: [insertions, deletions]}

    for line in lines:
        if len(line) == 0:
            continue

        if is_commit_line(line):
            # format '2012-12-12'
            year, month, day = map(int, line.split('-'))
            week = datetime.date(year, month, day).isocalendar()[1]

        if is_count_line(line):
            m = re.search('(\d+)\sinsertion', line)
            insertions = int(m.group(1)) if m else 0

            m = re.search('(\d+)\sdeletion', line)
            deletions = int(m.group(1)) if m else 0

            loc = week_loc.get(week, [0, 0])
            loc[0] += insertions
            loc[1] += deletions
            week_loc[week] = loc

    return week_loc


def build_coordinates(week_loc):
    insertion_coordinates = []
    deletion_coordinates = []

    for week, loc in week_loc.iteritems():
        print 'week: %s insertions: %-6s deletions: %-6s' \
            % (week, loc[0], loc[1])

        insertion_coordinates.append('(%s,%s)' % (week, loc[0]))
        deletion_coordinates.append('(%s,%s)' % (week, loc[1]))

    print '\ninsertions:'
    print ' '.join(insertion_coordinates)
    print
    print 'deletions:'
    print ' '.join(deletion_coordinates)

"""
\begin{tikzpicture}
\begin{axis}[
    height=6cm,
    width=10cm,
    ybar stacked,
    bar width=8pt,
    enlargelimits=0.15,
    legend style={at={(0.5,-0.20)},
      anchor=north,legend columns=-1},
    xlabel={Week},
    xlabel style={font=\footnotesize},
    ylabel={LoC changes},
    symbolic x coords={13, 14, 15, 16, 17, 18, 19,
        20, 21, 22, 23, 24, 25, 26, 27, 28},
    xtick=data,
    x tick label style={font=\footnotesize},
    y tick label style={font=\footnotesize},
    ]
\addplot+[ybar] plot coordinates {(13,838) (14,366) (15,568) (16,1056)
  (17,327) (18,451) (19,808) (20,873) (21,1173) (22,430) (23,793)
  (24,0) (25,1278) (26,1007) (27,203) (28,346)};
\addplot+[ybar] plot coordinates {(13,8) (14,69) (15,272) (16,98)
  (17,66) (18,106) (19,248) (20,231) (21,998) (22,301) (23,340)
  (24,0) (25,361) (26,289) (27,134) (28,172)};
\legend{insertions, deletions}
\end{axis}
\end{tikzpicture}
"""


def main(argv):
    if not argv:
        print 'usage: python gitloc.py <gitpath>'
        sys.exit(2)

    gitpath = argv[0]

    if not os.path.exists(gitpath):
        print 'Path "%s" not exist.' % gitpath
        sys.exit(2)

    os.chdir(gitpath)

    stdout = read_stdout(git_log_cmd)
    if stdout is None:
        raise Exception('Can\'t get any commit logs')

    lines = stdout.split('\n')
    week_loc = count_loc(lines)

    build_coordinates(week_loc)


if __name__ == '__main__':
    main(sys.argv[1:])
