print("✅ test.py started running")

from brain import run_brain

print("🧠 Calling brain...")

result = run_brain({
    "business": "Local Pilates studio",
    "goal": "Get more followers",
    "tone": "friendly"
})

print("🎉 RESULT:")
print(result)
