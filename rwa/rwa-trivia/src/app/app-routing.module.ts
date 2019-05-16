import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { CategoriesComponent, TagsComponent, QuestionsComponent, QuestionAddUpdateComponent } from './components';

const routes: Routes = [
  {
    path: '',
    redirectTo: '/categories',
    pathMatch: 'full'
  },
  {
    path: 'categories',
    component: CategoriesComponent
  },
  {
    path: 'tags',
    component: TagsComponent
  },
  {
    path: 'questions',
    component: QuestionsComponent
  },
  {
    path: 'question/add',
    component: QuestionAddUpdateComponent
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
