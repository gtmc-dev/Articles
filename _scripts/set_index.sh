#!/bin/bash

# THIS IS A ONE-TIME SCRIPT FOR DATA MIGRATION. DO NOT USE IT AGAIN UNLESS YOU KNOW WHAT YOU ARE DOING.

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EXCLUDE_FILES=("CONTRIBUTING.md" "CONTRIBUTING_CN.md" "Preface.md" "_Test Article.md")

is_excluded() {
	local file="$1"
	for excl in "${EXCLUDE_FILES[@]}"; do
		if [[ "$file" == "$excl" ]]; then
			return 0
		fi
	done
	return 1
}

is_readme() {
	local file="$1"
	[[ "$file" == */README.md ]] && return 0
	return 1
}

total=0
while IFS= read -r -d '' md; do
	rel="${md#$REPO_ROOT/}"

	[[ "$rel" == README.md ]] && continue

	if is_excluded "$(basename "$md")"; then
		continue
	fi

	if is_readme "$rel"; then
		continue
	fi

	filename=$(basename "$md")

	if [[ "$filename" =~ ^([0-9]+)- ]]; then
		num_str="${BASH_REMATCH[1]}"
		num=$((10#$num_str))

		if grep -q "^index:" "$md"; then
			sed -i '' "s/^index:.*/index: $num/" "$md"
		else
			sed -i '' "/^---$/,/^---$/ { /^is-advanced:/a\\index: $num
}" "$md"
		fi

		new_filename="${filename#"$num_str-"}"
		if [[ "$new_filename" != "$filename" ]]; then
			dir=$(dirname "$md")
			new_path="$dir/$new_filename"
			mv "$md" "$new_path"
			md="$new_path"
			rel="${md#$REPO_ROOT/}"
		fi

		echo "$rel: index=$num"
		((total++))
	fi
done < <(find "$REPO_ROOT" -name "*.md" -print0)

echo "Total: $total files updated"
