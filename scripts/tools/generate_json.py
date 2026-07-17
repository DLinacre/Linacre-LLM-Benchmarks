import json

data = {
    "Text & Chat": [
        {"name": "Claude Fable 5", "elo": 1507, "type": "paid"},
        {"name": "Claude Opus 4.6 (Thinking)", "elo": 1504, "type": "paid"},
        {"name": "Claude Opus 4.7 (Thinking)", "elo": 1503, "type": "paid"},
        {"name": "Claude Opus 4.6", "elo": 1498, "type": "paid"},
        {"name": "Claude Opus 4.7", "elo": 1494, "type": "paid"},
        {"name": "Metamuse Spark 1.1", "elo": 1493, "type": "free"},
        {"name": "Metamuse Spark", "elo": 1487, "type": "free"},
        {"name": "Gemini 3 Pro", "elo": 1486, "type": "paid"},
        {"name": "Kimi K3", "elo": 1486, "type": "paid"},
        {"name": "GPT 5.6 Sol (xHigh)", "elo": 1486, "type": "paid"},
        {"name": "Gemini 3.1 Pro (Preview)", "elo": 1485, "type": "paid"},
        {"name": "Claude Opus 4.8 (Thinking)", "elo": 1480, "type": "paid"},
        {"name": "GPT 5.5 (High)", "elo": 1479, "type": "paid"},
        {"name": "GPT 5.4 (High)", "elo": 1475, "type": "paid"},
        {"name": "Gemini 3.5 Flash (High)", "elo": 1470, "type": "paid"},
        {"name": "GPT 5.2 Chat (Latest)", "elo": 1468, "type": "paid"},
        {"name": "Qwen 3.7 Max", "elo": 1465, "type": "free"},
        {"name": "GPT 5.5", "elo": 1462, "type": "paid"},
        {"name": "Grok 4.20 (Beta 1)", "elo": 1460, "type": "paid"},
        {"name": "Gemini 3.5 Flash (Medium)", "elo": 1458, "type": "paid"},
        {"name": "GLM 5.1", "elo": 1440, "type": "free"},
        {"name": "DeepSeek V4 Pro", "elo": 1454, "type": "free"},
        {"name": "GLM 5.2 Max", "elo": 1468, "type": "free"}
    ],
    "WebDev & Code": [
        {"name": "Kimi K3", "elo": 1679, "type": "paid"},
        {"name": "Claude Fable 5", "elo": 1631, "type": "paid"},
        {"name": "GPT 5.6 Sol (xHigh)", "elo": 1618, "type": "paid"},
        {"name": "GLM 5.2 (Max)", "elo": 1587, "type": "free"},
        {"name": "Claude Opus 4.8 (Thinking)", "elo": 1562, "type": "paid"},
        {"name": "Grok 4.5", "elo": 1558, "type": "paid"},
        {"name": "Claude Opus 4.7 (Thinking)", "elo": 1558, "type": "paid"},
        {"name": "Claude Opus 4.7", "elo": 1555, "type": "paid"},
        {"name": "Claude Opus 4.6 (Thinking)", "elo": 1542, "type": "paid"},
        {"name": "Claude Sonnet 5 (High)", "elo": 1542, "type": "paid"},
        {"name": "GPT 5.5 (High)", "elo": 1519, "type": "paid"},
        {"name": "Metamuse Spark", "elo": 1500, "type": "free"}
    ],
    "Vision & Images": [
        {"name": "Claude Fable 5", "elo": 1318, "type": "paid"},
        {"name": "Claude Opus 4.7 (Thinking)", "elo": 1304, "type": "paid"},
        {"name": "Claude Opus 4.6 (Thinking)", "elo": 1299, "type": "paid"},
        {"name": "Claude Opus 4.7", "elo": 1299, "type": "paid"},
        {"name": "Claude Opus 4.6", "elo": 1298, "type": "paid"},
        {"name": "Metamuse Spark", "elo": 1295, "type": "free"},
        {"name": "Gemini 3 Pro", "elo": 1289, "type": "paid"},
        {"name": "GPT 5.5 (High)", "elo": 1286, "type": "paid"},
        {"name": "Claude Opus 4.8 (Thinking)", "elo": 1286, "type": "paid"},
        {"name": "Gemini 3.5 Flash (Medium)", "elo": 1286, "type": "paid"},
        {"name": "DeepSeek V4 Pro", "elo": 1260, "type": "free"}
    ]
}

# Sort all by ELO descending
for cat in data:
    data[cat].sort(key=lambda x: x["elo"], reverse=True)

with open('Linacre-LLM-Benchmarks/src/data/models.json', 'w') as f:
    json.dump(data, f, indent=4)
