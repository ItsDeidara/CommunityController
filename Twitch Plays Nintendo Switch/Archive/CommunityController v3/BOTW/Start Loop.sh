GREEN='\033[0;32m'
NC='\033[0m' # No Color

while :
do
	echo -e "${GREEN}Starting script${NC}\n"
	python3.6 main.py &
	PID=$!
	echo -e "${GREEN}Resting for 180 seconds${NC}\n"
	sleep 180
	echo -e "${GREEN}Stopping script${NC}\n"
	kill -9 $PID
done