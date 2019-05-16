import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent, CategoriesComponent } from './components';
import { CategoryService, QuestionService, TagService } from './services';
import { TagsComponent } from './components/tags/tags.component';
import { QuestionsComponent } from './components/questions/questions.component';

@NgModule({
  declarations: [
    AppComponent, CategoriesComponent, TagsComponent, QuestionsComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    AppRoutingModule
  ],
  providers: [
    CategoryService, QuestionService, TagService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
