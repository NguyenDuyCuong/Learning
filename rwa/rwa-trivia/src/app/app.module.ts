import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';

import 'hammerjs';
import { MaterialModule } from './material-extension';
import { FlexLayoutModule } from '@angular/flex-layout';

import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent, CategoriesComponent, TagsComponent, QuestionsComponent, QuestionAddUpdateComponent } from './components';
import { CategoryService, QuestionService, TagService } from './services';

@NgModule({
  declarations: [
    AppComponent, CategoriesComponent, TagsComponent, QuestionsComponent, QuestionAddUpdateComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    HttpClientModule,
    MaterialModule,
    FlexLayoutModule,
    FormsModule, ReactiveFormsModule,
    AppRoutingModule
  ],
  providers: [
    CategoryService, QuestionService, TagService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
