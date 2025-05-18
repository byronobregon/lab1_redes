package main

import (
	"encoding/json"
	"fmt"
	"math/rand"
	"net"
	"os"
	"strconv"
	"strings"
	"time"
)

func main() {
	mainPort := 6000
	conn := createConnection(mainPort)
	defer conn.Close()

	fmt.Println("Server listening to UDP: ", mainPort)

	buffer := make([]byte, 1024)
	var gameNumber int
	var gameActive bool = false

	for {
		n, remoteAddr, err := conn.ReadFromUDP(buffer)
		if err != nil {
			fmt.Println("Error reading from middle server response:", err)
			continue
		}

		var message map[string]string
		err = json.Unmarshal(buffer[:n], &message)
		if err != nil {
			fmt.Println("Error parsing JSON:", err)
			continue
		}

		if action, exists := message["action"]; exists && action == "reset" {

			response := map[string]string{
				"message": "Game Reset.",
				"status":  "reset",
			}

			jsonResponse, _ := json.Marshal(response)
			_, err = conn.WriteToUDP(jsonResponse, remoteAddr)
			if err != nil {
				fmt.Println("Error sending response:", err)
				continue
			}

			gameActive = false

			fmt.Println("Server is resetting.")
		}

		if action, exists := message["action"]; exists && action == "stop" {

			response := map[string]string{
				"message": "Game stoped.",
				"status":  "closing",
			}

			jsonResponse, _ := json.Marshal(response)
			_, err = conn.WriteToUDP(jsonResponse, remoteAddr)
			if err != nil {
				fmt.Println("Error sending response:", err)
				continue
			}

			conn.Close()
			fmt.Println("Server is closing.")
			os.Exit(0)
		}

		if action, exists := message["action"]; exists && action == "start" {
			if gameActive == true {
				response := map[string]string{
					"message": "Game currently active.",
					"status":  "busy",
				}

				jsonResponse, _ := json.Marshal(response)
				_, err = conn.WriteToUDP(jsonResponse, remoteAddr)
				if err != nil {
					fmt.Println("Error sending response:", err)
					continue
				}
			} else {
				newPort := generateRandomPort(time.Now().UTC().UnixNano())
				//newPort := 6000
				gameNumber = rand.Intn(20)
				gameActive = true
				fmt.Printf("New game started. number: %d\n", gameNumber)

				response := map[string]string{
					"message": "Game started.",
					"port":    strconv.Itoa(newPort),
					"status":  "playing",
				}

				jsonResponse, _ := json.Marshal(response)
				_, err = conn.WriteToUDP(jsonResponse, remoteAddr)
				if err != nil {
					fmt.Println("Error sending response:", err)
					continue
				}

				conn.Close()
				conn = createConnection(newPort)
				fmt.Println("Server is now listening at UDP port:", newPort)
				continue
			}
		}

		number, exists := message["number"]
		if !exists {
			fmt.Println("No number field in message")
			continue
		}
		// remove trash trailing
		cleanNumber := strings.TrimSpace(number)
		fmt.Printf("Recibido: %s desde %s\n", cleanNumber, remoteAddr)

		num, err := strconv.Atoi(cleanNumber)
		if err != nil {
			fmt.Println("Error converting string to number.", err)
			return
		}

		newPort := generateRandomPort(time.Now().UTC().UnixNano())
		//newPort := 6000
		result := checkNumber(gameNumber, num)

		status := "playing"
		if result == "same" {
			status = "won"
		}

		data := map[string]string{
			"message": result,
			"port":    strconv.Itoa(newPort),
			"status":  status,
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
		return "smaller"
	} else if number == gameNumber {
		return "same"
	} else {
		return "bigger"
	}
}