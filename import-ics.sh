#!/bin/sh

DIR=$(cd "$(dirname "$0")" && pwd)

URL="$1"
ORG_OUT="$2"
USERNAME="$3"

PYCAL2ORG="${DIR}/pycal2org.py"

usage() {
  echo "$0 <URL> </path/to/output.org> [username]"
  echo "Fetch an ICS file from an URL and transform it to a org-mode file."
  echo "Username is optional, for HTTP authentication: if set, a password will be prompted for."
  exit 1
}

fail() {
  echo "$@" >&2
  exit 1
}

[ -z "$ORG_OUT" ] && usage

[ -n "$USERNAME" ] && CURL="curl -u $USERNAME" || CURL="curl"

TMPFILE="$(mktemp)"

$CURL -s -f "$URL" > "$TMPFILE" || fail "Failed to fetch calendar"

$PYCAL2ORG "$TMPFILE" > "$TMPFILE".org || fail "Failed to transform ICS into org-file"
cp "$TMPFILE".org "$ORG_OUT"
rm "$TMPFILE" "$TMPFILE".org

echo "Successfully downloaded and transformed '$URL' to '$ORG_OUT'"
