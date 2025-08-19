package main

import "C"

import (
	"fmt"
	"os"

	"github.com/aws/session-manager-plugin/src/datachannel"
	"github.com/aws/session-manager-plugin/src/log"
	"github.com/aws/session-manager-plugin/src/sessionmanagerplugin/session"
	_ "github.com/aws/session-manager-plugin/src/sessionmanagerplugin/session/portsession"
	_ "github.com/aws/session-manager-plugin/src/sessionmanagerplugin/session/shellsession"
)

//export StartSession
func StartSession(sessionId *C.char, url *C.char, tokenValue *C.char, endpoint *C.char, clientId *C.char, targetId *C.char) int {
	// Simple implementation of StartSession from session-manager-plugin, for POC purposes right now
	ssmSession := new(session.Session)
	ssmSession.SessionId = C.GoString(sessionId)
	ssmSession.StreamUrl = C.GoString(url)
	ssmSession.TokenValue = C.GoString(tokenValue)
	ssmSession.Endpoint = C.GoString(endpoint)
	ssmSession.ClientId = C.GoString(clientId)
	ssmSession.TargetId = C.GoString(targetId)
	ssmSession.DataChannel = &datachannel.DataChannel{}
	err := ssmSession.Execute(log.Logger(false, C.GoString(clientId)))
	if err != nil {
		fmt.Fprintln(os.Stderr, "StartSession error:", err)
		return 1
	}
	return 0
}

func main() {}
