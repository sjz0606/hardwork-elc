#!/bin/bash
# Hosting diski/inode limiti kichik: Django tarjimalaridan faqat uz, ru, en qoldiriladi (~20 MB, ~2700 fayl tejaladi).
SP=$(python -c 'import django,os;print(os.path.dirname(django.__file__))') || exit 0
find "$SP" -type d -path '*/locale/*' -prune -name '*' | while read -r d; do
  case "$(basename "$d")" in uz|ru|en|en_GB) ;; *) rm -rf "$d" ;; esac
done
