package mongoUtils

import (
	"context"
	"fmt"
	"log"
	"sync"
	"time"

	"github.com/louieh/FakeCourseBook/config"
	"github.com/louieh/FakeCourseBook/models"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

var (
	mongoClient *mongo.Client
	once        sync.Once
)

func createMongoClient() *mongo.Client {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	client, err := mongo.Connect(ctx, options.Client().ApplyURI(fmt.Sprintf("mongodb://%s:%d", config.AppConfig.DBMongoHost, config.AppConfig.DBMongoPort))) // "mongodb://localhost:27017"
	if err != nil {
		panic(err)
	}
	return client
}

func GetMongoClient() *mongo.Client {
	once.Do(func() {
		mongoClient = createMongoClient()
	})
	return mongoClient
}

type findType interface {
	models.ProfessorsList | models.CoursesList | models.CourseForSearch | models.CourseForGrade | models.CourseForSpeed
}

func DoFind[T findType](ctx context.Context, collName string, filter any, opts *options.FindOptions, container *[]T) {
	client := GetMongoClient()
	// TODO deal with that
	// defer func() {
	// 	if err := client.Disconnect(ctx); err != nil {
	// 		panic(err)
	// 	}
	// }()
	collection := client.Database(config.AppConfig.DBMongoDB).Collection(collName)
	cur, err := collection.Find(context.Background(), filter, opts)
	if err != nil {
		log.Fatal(err)
	}
	// defer cur.Close(context.Background())
	for cur.Next(context.Background()) {
		// To decode into a struct, use cursor.Decode()
		// var result bson.M
		var result T
		err := cur.Decode(&result)
		if err != nil {
			log.Fatal(err)
		}
		// do something with result...
		// fmt.Println("result: ", result)
		*container = append(*container, result)
	}
	if err := cur.Err(); err != nil {
		log.Fatal(err)
	}
}
