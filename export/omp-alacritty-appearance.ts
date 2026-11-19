import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";
import { getActiveTerminal } from "@oh-my-pi/pi-tui/active-terminal";
import { statSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

export default function alacrittyAppearance(pi: ExtensionAPI) {
	if (!process.env.ALACRITTY_WINDOW_ID || process.env.TMUX) return;

	// The desktop scheduler touches the primary config after switching its import.
	// Alacritty 0.17 reloads it without sending an appearance notification.
	const config = join(
		process.env.XDG_CONFIG_HOME || join(homedir(), ".config"),
		"alacritty",
		"alacritty.toml",
	);
	let stop: (() => void) | undefined;
	let observed: bigint | undefined;
	let refreshed: bigint | undefined;
	const refresh = () => {
		const current = statSync(config, { bigint: true, throwIfNoEntry: false })?.mtimeNs;
		if (current !== undefined && current === observed && current !== refreshed) {
			if (getActiveTerminal()?.refreshAppearance() !== undefined) refreshed = current;
		}
		observed = current;
	};

	pi.on("session_start", (_event, ctx) => {
		if (!ctx.hasUI || stop) return;
		const timer = setInterval(refresh, 750);
		timer.unref();
		stop = () => clearInterval(timer);
	});
	pi.on("session_shutdown", () => {
		stop?.();
		stop = undefined;
		observed = refreshed = undefined;
	});
}
