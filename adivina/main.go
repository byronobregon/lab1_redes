package main

import (
	"encoding/json"
	"fmt"
	"math/rand"
	"net"
	"strconv"
	"strings"
	"time"
)

func main() {
	mainPort := 6000
	gameNumber := rand.Intn(20)
	fmt.Printf("Game number: %d\n", gameNumber)

	conn := createConnection(mainPort)

	buffer := make([]byte, 1024)
	fmt.Println("Server listening to UDP mainPort: ", mainPort)

	for {
		n, remoteAddr, err := conn.ReadFromUDP(buffer)
		if err != nil {
			fmt.Println("Error reading from middle server response:", err)
			continue
		}

		numero := string(buffer[:n])
		// remove trash trailing
		cleanNumber := strings.TrimSpace(numero)
		fmt.Printf("Recibido: %s desde %s\n", cleanNumber, remoteAddr)

		num, err := strconv.Atoi(cleanNumber)
		if err != nil {
			fmt.Println("Error converting string to number.", err)
			return
		}

		newPort := generateRandomPort(time.Now().UTC().UnixNano())

		// TODO status should tell if the server is shutting down or working, for this we need more info from python
		data := map[string]string{
			"message": checkNumber(gameNumber, num),
			"address": conn.LocalAddr().String(),
			"port":    strconv.Itoa(newPort),
			"status":  "working",
		}
		jsonData, _ := json.Marshal(data)

		_, err = conn.WriteToUDP(jsonData, remoteAddr)

		conn.Close()
		conn = createConnection(newPort)
		fmt.Println("Server is now listening at UDP: ", newPort)
	}
}

func generateRandomPort(seed int64) int {
	rand.Seed(seed)
	return rand.Intn(65535-8000+1) + 8000
}

func createConnection(port int) *net.UDPConn {
	addr := net.UDPAddr{
		Port: port,
		IP:   net.ParseIP("0.0.0.0"),
	}
	conn, err := net.ListenUDP("udp", &addr)
	if err != nil {
		panic(err)
	}
	return conn
}

func checkNumber(gameNumber int, number int) string {
	if number > gameNumber {
		return "bigger"
	} else if number == gameNumber {
		return "same"
	} else {
		return "smaller"
	}
}
