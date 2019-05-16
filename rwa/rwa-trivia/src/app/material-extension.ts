import { NgModule } from '@angular/core';
import {
    MatButtonModule, MatCheckboxModule,
    MatSidenavModule, MatListModule, MatIconModule, MatToolbarModule,
    MatCardModule, MatChipsModule
} from '@angular/material';

@NgModule({
    imports: [
        MatButtonModule, MatCheckboxModule, MatSidenavModule, MatListModule, MatIconModule, MatToolbarModule, MatCardModule, MatChipsModule
    ],
    exports: [
        MatButtonModule, MatCheckboxModule, MatSidenavModule, MatListModule, MatIconModule, MatToolbarModule, MatCardModule, MatChipsModule
    ],
})
export class MaterialModule { }
