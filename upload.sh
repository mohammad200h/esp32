#!/usr/bin/env bash
# Auto-detect Silicon Labs CP210x UART (USB 10c4:ea60). Override with PORT=/dev/... if needed.

CP210_VENDOR_ID="10c4"
CP210_MODEL_ID="ea60"

is_cp210_bridge() {
	local dev=$1
	[[ -c "$dev" ]] || return 1
	local props
	props=$(udevadm info -q property -n "$dev" 2>/dev/null) || return 1
	grep -q "^ID_VENDOR_ID=${CP210_VENDOR_ID}$" <<<"$props" || return 1
	grep -q "^ID_MODEL_ID=${CP210_MODEL_ID}$" <<<"$props" || return 1
}

find_cp210_port() {
	local dev
	shopt -s nullglob
	for dev in /dev/ttyUSB*; do
		if is_cp210_bridge "$dev"; then
			echo "$dev"
			return 0
		fi
	done
	return 1
}

resolve_port() {
	if [[ -n "${PORT:-}" ]]; then
		echo "$PORT"
		return 0
	fi
	local n=0
	while true; do
		local p
		if p=$(find_cp210_port); then
			if (( n > 0 )); then
				echo "Found CP210x at $p" >&2
			fi
			echo "$p"
			return 0
		fi
		n=$((n + 1))
		if (( n == 1 )); then
			echo "No Silicon Labs CP210x serial device yet (USB ${CP210_VENDOR_ID}:${CP210_MODEL_ID})." >&2
			echo "Plug in the board — this script will keep checking. Override with PORT=/dev/ttyUSB0 $0 ..." >&2
		fi
		echo "Still waiting for CP210x… attempt $n (next check in 2s, Ctrl+C to abort)" >&2
		sleep 2
		
	done
}

PORT="$(resolve_port)"
PYTHON_FILE="${1:-blink.py}"

# ampy run only executes that file; imports are resolved from files on the board.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1
for dep in servo.py rotary_encoder_knobe.py; do
	if [[ -f "$dep" ]]; then
		ampy --port "$PORT" put "$dep"
	fi
done

ampy --port "$PORT" run "$PYTHON_FILE"
