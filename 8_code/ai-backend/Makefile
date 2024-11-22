base_url:=http://localhost:8000
api_key:=api_key
endpoint:=chat
#endpoint:=chat_mock

init:
	poetry install

run:
	poetry run python start_service.py

post_windows:
	curl -X POST $(base_url)/$(endpoint) -H "Content-Type: application/json" -H "X-Chat-Key: $(api_key)" -d "{\"sessionId\": \"GUID\", \"customerId\": 1232, \"isAuthenticated\": true, \"chatMessage\": \"Where is my order 2314\"}"

post:
	curl -X POST $(base_url)/$(endpoint) \
	-H "Content-Type: application/json" \
	-H "X-Chat-Key: api_key" \
	-d "{\"sessionId\": \"GUID\", \"customerId\": 1232, \"isAuthenticated\": true, \"chatMessage\": \"Where is my order\"}"


