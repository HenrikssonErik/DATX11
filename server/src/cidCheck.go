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

	_name := "";
	_affilitation := "";
	_title := ""; 

	for _, attr := range res.Entries[0].Attributes {
		if attr.Name == "cn"{
			_name = attr.Values[0] + ",";
		} else if attr.Name == "eduPersonAffiliation"{
			_affilitation = attr.Name + ":" + attr.Values[0] + " " + attr.Values[1] + ",";
		} else if attr.Name == "title"{
			_title = attr.Name + ":" + attr.Values[0];
		}
	}

	fmt.Println(_name + _affilitation + _title)
}
