#!/bin/bash

# 测试Persona API
echo "=========================================="
echo "🧪 测试Persona API"
echo "=========================================="

cd /Users/loubicheng/project/discrimination/backend
source venv/bin/activate

# 1. 获取书籍列表
echo ""
echo "📚 1. 获取书籍列表..."
BOOKS=$(curl -s http://localhost:8000/api/books | python3 -c "import sys, json; data=json.load(sys.stdin); print(json.dumps(data.get('data', {}).get('books', [])))")
BOOK_COUNT=$(echo "$BOOKS" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
echo "找到 $BOOK_COUNT 本书"

if [ "$BOOK_COUNT" -eq "0" ]; then
  echo "❌ 没有找到书籍，请先上传书籍"
  exit 1
fi

# 获取第一本书的ID
FIRST_BOOK_ID=$(echo "$BOOKS" | python3 -c "import sys, json; books=json.load(sys.stdin); print(books[0]['book_id'])")
FIRST_BOOK_TITLE=$(echo "$BOOKS" | python3 -c "import sys, json; books=json.load(sys.stdin); print(books[0]['title'])")

echo "  选择书籍: $FIRST_BOOK_TITLE (ID: $FIRST_BOOK_ID)"

# 2. 测试创建Persona
echo ""
echo "🎭 2. 测试创建Persona..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/personas \
  -H "Content-Type: application/json" \
  -d "{\"book_id\": \"$FIRST_BOOK_ID\"}")

echo "  响应: $RESPONSE"

# 提取persona_id
PERSONA_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('persona_id', 'N/A'))")

if [ "$PERSONA_ID" != "N/A" ]; then
  echo "  ✅ Persona创建成功!"
  echo "  Persona ID: $PERSONA_ID"
else
  echo "  ❌ Persona创建失败"
  exit 1
fi

# 3. 测试获取Persona详情
echo ""
echo "📖 3. 测试获取Persona详情..."
DETAILS=$(curl -s http://localhost:8000/api/personas/$PERSONA_ID)
echo "  响应: $DETAILS"

AUTHOR_NAME=$(echo "$DETAILS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('author_name', 'N/A'))")
echo "  ✅ 作者姓名: $AUTHOR_NAME"

# 4. 测试生成System Prompt
echo ""
echo "✨ 4. 测试生成System Prompt..."
PROMPT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/personas/$PERSONA_ID/generate-prompt)
echo "  响应: $PROMPT_RESPONSE"

echo ""
echo "=========================================="
echo "✅ 所有测试通过!"
echo "=========================================="
echo ""
echo "📝 测试结果:"
echo "  - Persona ID: $PERSONA_ID"
echo "  - 作者姓名: $AUTHOR_NAME"
echo ""
