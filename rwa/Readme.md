# Links
* https://blog.realworldfullstack.io/real-world-angular-part-0-from-zero-to-cli-ng-a2ff646b90cc
* https://github.com/anihalaney/rwa-trivia

# Steps
## Part #1
1. Move app.component to components/app
2. Create models
3. Use json-server provides rest end points for json data

    ```
    npm install --save-dev json-server
    ```
4. create db.json
5. add script run api server in package.json

    `"api": "json-server --watch src/db.json"`
6. service -> components -> router
## Part #2
1. Add angular material to our project, along with hammerjs (used for gestures on touch devices)
    ```
    npm install --save @angular/material @angular/cdk @angular/animations hammerjs
    npm install --save-dev @types/hammerjs
    npm install --save @angular/flex-layout
    ```
2. Create material-extension.ts, material-icon,
3. Custom theme in angular.json

## Part #4
1. State management

    `npm install --save @ngrx/core @ngrx/effects @ngrx/store`

# Ng cli
1. Genarate component
    ```
    ng g component --skipTests=true --skipImport=true --flat=true --selector=xxx
    ```

# Learn
## View encapsulation strategy
### Shadow DOM
Shadow DOM is part of the Web Components standard and enables DOM tree and style encapsulation.

DOM tree and style encapsulation? What does that even mean? Well, it basically means that Shadow DOM allows us to hide DOM logic behind other elements. Addition to that, it enables us to apply scoped styles to elements without them bleeding out to the outer world.

### View Encapsulation Types
* ViewEncapsulation.None - No Shadow DOM at all. Therefore, also no style encapsulation.
* ViewEncapsulation.Emulated - No Shadow DOM but style encapsulation emulation.
* ViewEncapsulation.Native - Native Shadow DOM with all it’s goodness.

## @types/hammerjs
## Reactive forms
Reactive forms provide a model-driven approach to handling form inputs whose values change over time
### FormGroup
### FormBuilder
### Form validator
Angular allow us to pass in custom validators in order to validate data in our forms. There are two types of validation functions, we can pass for each formcontrol, a synchronous (for synchronous client-side validations) validator and an asynchronous (if we need to make server calls to validate data) one.

Angular sets properties (such as value, status, pristine & untouched) on the FormControl & FormGroup objects based on it’s validity and input status in the browser. It also sets appropriate css classes like ng-valid, ng-invalid, ng-pristine, ng-touched to the form elements so the appearance of the page can easily be customized based on the css.

## Redux Principles
### Single source of truth - The state of your entire application (SPA in our case) is stored in an object tree within a single store.
### State is read-only - The only way to change the state is to emit an action, an object describing what happened.
### Changes to the store are made with pure functions (reducers)

## Firebase
## Route Guards

# Notes
1. Move the app.component to it’s own app folder under src/app/components.
2. Use of index.ts in each of the high level folders (components, model, services) that export all the classes in these folders so you don’t have to reference individual files in your import.
3. Can put all references in a file and include (`the addition of rxjs-extensions to the app folder`)
