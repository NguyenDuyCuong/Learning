import { NgModule } from '@angular/core';
import {
    MatButtonModule, MatCheckboxModule,
    MatSidenavModule, MatListModule, MatIconModule, MatToolbarModule,
    MatCardModule, MatChipsModule, MatInputModule, MatSelectModule
} from '@angular/material';

@NgModule({
    imports: [
        MatButtonModule, MatCheckboxModule, MatSidenavModule, MatListModule,
        MatIconModule, MatToolbarModule, MatCardModule, MatChipsModule,
        MatInputModule, MatSelectModule
    ],
    exports: [
        MatButtonModule, MatCheckboxModule, MatSidenavModule, MatListModule,
        MatIconModule, MatToolbarModule, MatCardModule, MatChipsModule,
        MatInputModule, MatSelectModule
    ],
})
export class MaterialModule { }
