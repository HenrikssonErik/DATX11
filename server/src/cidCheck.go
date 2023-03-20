package main

import (
	"crypto/tls"
	"fmt"
    "os"
	"gopkg.in/ldap.v2"
)

func main() {
	conn, err := ldap.DialTLS("tcp", "ldap.chalmers.se:636", &tls.Config{
		ServerName:         "ldap.chalmers.se",
		InsecureSkipVerify: true,
	})
	
	if err != nil {
		fmt.Println(err)
		return
	}
	defer conn.Close()

	printUserAttributes(conn, os.Args[1])

}

func printUserAttributes(conn *ldap.Conn, cid string) {
	req := ldap.NewSearchRequest(
		"ou=people,dc=chalmers,dc=se",
		ldap.ScopeWholeSubtree,
		ldap.NeverDerefAliases, 0, 0, false,
		fmt.Sprintf("(uid=%s)", cid),
		[]string{"*"}, nil)

		
	res, err := conn.Search(req)
	if err != nil {
		fmt.Println(err)
		return
	}

	if len(res.Entries) < 1 {
		fmt.Println("No entries found")
		return
	}

	for _, attr := range res.Entries[0].Attributes {
		if(attr.Name == "uid"){
			fmt.Println("User Exists")
		}
	}
}
