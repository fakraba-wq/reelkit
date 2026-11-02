# 🔌 Using MCP servers with reelkit

MCP (Model Context Protocol) lets Claude Code call external tools: stock sources, media generators, file helpers. reelkit works without any MCP server; MCP just gives Claude more things to reach for during an edit.

```
Claude Code ──(MCP)──► your media server ──► assets / renders ──► back into the edit
```

## 1 · Add a server 🧰
Local (stdio) server:
```bash
claude mcp add my-media -- npx -y <package-name>
```
Remote (HTTP) server:
```bash
claude mcp add --transport http my-media https://example.com/mcp
```
Then check it:
```bash
claude mcp list
```
Inside Claude Code, run `/mcp` to see connection status and approve sign-in if the server needs OAuth.

## 2 · Keep secrets out of the repo 🔐
Pass keys through environment variables, never into files you commit:
```bash
claude mcp add my-media --env MEDIA_API_KEY=$MEDIA_API_KEY -- npx -y <package-name>
```

## 3 · Use it in the pipeline 🎬
Typical prompts once connected:
- "Run the `talking-head-reel` skill on `raw.mp4`. For every product or brand the speaker names, fetch a real image through the media MCP server."
- "Find a short B-roll clip for each sentence in `captions.json` and list the source and licence."

## 4 · Hexfield / hex-file servers 🧪
If you use a Hexfield-style MCP server for binary or hex-level file work (inspecting container headers, checking codec bytes, repairing broken clips), add it the same way as in step 1 and ask Claude to call its tools before the silence cutter, for example to confirm a file is a valid MP4 before processing.

> Note: server names and tool lists differ per vendor. Run `/mcp` to see the exact tools your server exposes and refer to its own documentation for arguments.

## 5 · Troubleshooting 🛠️
| Symptom | Fix |
|---|---|
| Server shows "failed" in `/mcp` | Re-run the add command and check the URL or package name |
| "needs authentication" | Run `/mcp` and complete the sign-in |
| Tool not used | Mention the server by name in your prompt |
| Key leaked into git | Rotate it immediately, then add the file to `.gitignore` |
