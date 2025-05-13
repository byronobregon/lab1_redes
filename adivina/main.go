package main

import (
	"encoding/json"
	"fmt"
	"net"
	// "os"
	"math/rand"
	"time"
)

func main() {
	port := 6000

	// fmt.Println(newPort(time.Now().UnixNano()))

	conn := createConnection(port)


	buffer := make([]byte, 1024)
	fmt.Println("Servidor adivina escuchando UDP en el puerto", port)

	for {
		n, remoteAddr, err := conn.ReadFromUDP(buffer)
		if err != nil {
			fmt.Println("Error leyendo:", err)
			continue
		}

		numero := string(buffer[:n])
		fmt.Printf("Recibido: %s desde %s\n", numero, remoteAddr)

		newPort := newPort(time.Now().UnixNano())

		// Crear JSON con valor entero
		data := map[string]interface{}{
			"message": "ping",
			"newPort": newPort,
		}
		jsonData, _ := json.Marshal(data)

		conn.Close()
		conn := createConnection(newPort)
		_, err = conn.WriteToUDP([]byte(jsonData), remoteAddr)
		// if err == nil {
		// 	fmt.Println("Servidor cierra la conexión")
		// 	conn.Close()
		// }
	}
}

func atoiOrFallback(str string, fallback int) int {
	n, err := fmt.Sscanf(str, "%d", &fallback)
	if err != nil || n != 1 {
		return fallback
	}
	return fallback
}

func newPort(seed int64) int {
	rand.Seed(seed)
	return (rand.Intn(65535-8000+1) + 8000)
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
