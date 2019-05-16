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

# Ng cli
1. Genarate component
    `ng g component --skipTests=true --skipImport=true --selector=xxx`

# Learn
## View encapsulation strategy
### Shadow DOM
    Shadow DOM is part of the Web Components standard and enables DOM tree and style encapsulation.

    DOM tree and style encapsulation? What does that even mean? Well, it basically means that Shadow DOM allows us to hide DOM logic behind other elements. Addition to that, it enables us to apply scoped styles to elements without them bleeding out to the outer world.
### View Encapsulation Types
* ViewEncapsulation.None - No Shadow DOM at all. Therefore, also no style encapsulation.
* ViewEncapsulation.Emulated - No Shadow DOM but style encapsulation emulation.
* ViewEncapsulation.Native - Native Shadow DOM with all it’s goodness.

# Notes
1. Move the app.component to it’s own app folder under src/app/components.
2. Use of index.ts in each of the high level folders (components, model, services) that export all the classes in these folders so you don’t have to reference individual files in your import.
3. Can put all references in a file and include (`the addition of rxjs-extensions to the app folder`)
