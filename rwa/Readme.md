# Links
* https://blog.realworldfullstack.io/real-world-angular-part-0-from-zero-to-cli-ng-a2ff646b90cc
* https://github.com/anihalaney/rwa-trivia

# Steps
## Part 1
1. Move app.component to components/app
2. Create models
3. Use json-server provides rest end points for json data

    `npm install --save-dev json-server`
4. create db.json
5. add script run api server in package.json

    `"api": "json-server --watch src/db.json"`
6.

# Notes
1. Move the app.component to it’s own app folder under src/app/components.
2. Use of index.ts in each of the high level folders (components, model, services) that export all the classes in these folders so you don’t have to reference individual files in your import.
