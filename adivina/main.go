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
	// Puerto inicial del servidor
	mainPort := 6000

	// Crear la conexión UDP
	conn := createConnection(mainPort)
	defer conn.Close()

	fmt.Println("Server listening to UDP: ", mainPort)

	buffer := make([]byte, 1024)
	var gameNumber int
	var gameActive bool = false

	for {
		// Leer datos desde la conexión UDP
		n, remoteAddr, err := conn.ReadFromUDP(buffer)
		if err != nil {
			fmt.Println("Error reading from middle server response:", err)
			continue
		}

		// Parsear el mensaje JSON recibido
		var message map[string]string
		err = json.Unmarshal(buffer[:n], &message)
		if err != nil {
			fmt.Println("Error parsing JSON:", err)
			continue
		}

		// Manejar la acción 'stop' para detener el servidor
		if action, exists := message["action"]; exists && action == "stop" {
			sendMessage("Game stopped.", "closing", mainPort, conn, remoteAddr)

			// Cerrar conexión y finalizar el programa
			conn.Close()
			fmt.Println("Server is closing.")
			os.Exit(0)
		}

		if action, exists := message["action"]; exists && action == "start" {
			if gameActive {
				sendMessage("Game currently active.", "busy", mainPort, conn, remoteAddr)
			} else {

				// Generar un nuevo puerto aleatorio para el juego
				newPort := generateRandomPort(time.Now().UTC().UnixNano())
				// newPort := mainPort // TODO: no olvidar eliminar

				gameNumber = rand.Intn(100)
				gameActive = true
				fmt.Printf("New game started. number: %d\n", gameNumber)

				sendMessage("Game started.", "playing", newPort, conn, remoteAddr)

				conn.Close()
				conn = createConnection(newPort)
				fmt.Println("Server is now listening at UDP port:", newPort)
				continue
			}
		}

		// Procesar los intentos del jugador
		number, exists := message["number"]
		if !exists {
			fmt.Println("No number field in message")
			continue
		}
		// remove trash trailing
		cleanNumber := strings.TrimSpace(number)
		fmt.Printf("Recibido: %s desde %s\n", cleanNumber, remoteAddr)

		newPort := generateRandomPort(time.Now().UTC().UnixNano())
		// newPort := 6000
		status := "playing"

		num, err := strconv.Atoi(cleanNumber)
		if err != nil {
			message := "Error al convertir texto a número."
			fmt.Println(message, err)
			sendMessage(message, status, newPort, conn, remoteAddr)
		} else {
			result := checkNumber(gameNumber, num)
			if result == "same" {
				status = "won"
			}

			sendMessage(result, status, newPort, conn, remoteAddr)
		}

		conn.Close()
		conn = createConnection(newPort)
		fmt.Println("Server is now listening at UDP: ", newPort)
	}
}

func sendMessage(message string, status string, newPort int, conn *net.UDPConn, remoteAddr *net.UDPAddr) {

	data := map[string]string{
		"message": message,
		"address": conn.LocalAddr().String(),
		"port":    strconv.Itoa(newPort),
		// "port":    strconv.Itoa(mainPort),
		"status": status,
	}
	jsonData, _ := json.Marshal(data)
	_, err := conn.WriteToUDP(jsonData, remoteAddr)
	if err != nil {
		fmt.Println("Error sending response:", err)
	}
}

func generateRandomPort(seed int64) int {
	rand.Seed(seed)
	return rand.Intn(65535-8000+1) + 8000
}

// Crear una conexión UDP en el puerto especificado
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

// Verificar si el número enviado por el jugador es mayor, menor o igual al número generado
func checkNumber(gameNumber int, number int) string {
	if number > gameNumber {
		return "smaller"
	} else if number == gameNumber {
		return "same"
	} else {
		return "bigger"
	}
}
