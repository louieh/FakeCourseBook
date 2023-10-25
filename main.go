package main

import (
    "net/http"
    "context"
    "log"
    "time"
    "fmt"

    "github.com/gin-gonic/gin"
    "go.mongodb.org/mongo-driver/bson"
    "go.mongodb.org/mongo-driver/mongo"
    "go.mongodb.org/mongo-driver/mongo/options"
//     "go.mongodb.org/mongo-driver/mongo/readpref"
    "go.mongodb.org/mongo-driver/bson/primitive"
)

type album struct {
    ID     string  `json:"id"`
    Title  string  `json:"title"`
    Artist string  `json:"artist"`
    Price  float64 `json:"price"`
}

var albums = []album{
    {ID: "1", Title: "Blue Train", Artist: "John Coltrane", Price: 56.99},
    {ID: "2", Title: "Jeru", Artist: "Gerry Mulligan", Price: 17.99},
    {ID: "3", Title: "Sarah Vaughan and Clifford Brown", Artist: "Sarah Vaughan", Price: 39.99},
}

func getAlbums(c *gin.Context) {
    c.IndentedJSON(http.StatusOK, albums)
}

func testMongo(c *gin.Context) {
    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()
    client, err := mongo.Connect(ctx, options.Client().ApplyURI("mongodb://localhost:27017"))
    defer func() {
    if err = client.Disconnect(ctx); err != nil {
        panic(err)
        }
    }()
    collection := client.Database("Coursebook").Collection("test")

    cur, err := collection.Find(context.Background(), bson.D{})
    if err != nil { log.Fatal(err) }
    defer cur.Close(context.Background())
    for cur.Next(context.Background()) {
        // To decode into a struct, use cursor.Decode()
        result := struct {
            ID   primitive.ObjectID `bson:"_id"`
            KeyA string            `bson:"key_a"`
            KeyB string            `bson:"key_b"`
        }{}
        err := cur.Decode(&result)
        if err != nil { log.Fatal(err) }
        // do something with result...
        fmt.Println("result.KeyA: ", result.KeyA)
        // To get the raw bson bytes use cursor.Current
        raw := cur.Current
        // do something with raw...
        fmt.Println("row: ", raw)
        }
        if err := cur.Err(); err != nil {
            log.Fatal(err)
        }
}

func main() {
    router := gin.Default()
    router.GET("/albums", getAlbums)
    router.GET("/testMongo", testMongo)

    router.Run("localhost:8080")
}