import { NgModule } from '@angular/core';
import { BrowserModule, provideClientHydration } from '@angular/platform-browser';
import { RouterModule, Routes } from '@angular/router';
import { SignupComponent } from './signup/signup.component';
import { LoginComponent } from './login/login.component';
import { MainComponent } from './main/main.component';
import { StockInvestmentService } from './services/stock-investment.service';

import { FormsModule,ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule, HTTP_INTERCEPTORS  } from '@angular/common/http';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatTableModule } from '@angular/material/table';
import {MatTabsModule} from '@angular/material/tabs';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { DatePipe } from '@angular/common';
import { NgChartsModule} from 'ng2-charts';
import { NgxChartsModule } from '@swimlane/ngx-charts';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomeComponent } from './home/home.component';
import { PortfolioComponent } from './portfolio/portfolio.component';
import { WatchListComponent } from './watch-list/watch-list.component';
import { PerformanceComponent } from './performance/performance.component';

export const routes: Routes = [
  { path: 'signup', component: SignupComponent },
  { path: 'login', component: LoginComponent },
  { path: 'main', component: MainComponent},
  { path: 'home', component: HomeComponent},
  { path: 'watchList', component: WatchListComponent},
  { path: 'portfolio', component: PortfolioComponent},
  { path: 'performance', component: PerformanceComponent},
  { path: '', redirectTo: '/login', pathMatch: 'full' },
];

@NgModule({
  declarations: [
    AppComponent,
    SignupComponent,
    LoginComponent,
    MainComponent,
    HomeComponent,
    PortfolioComponent,
    WatchListComponent,
    PerformanceComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    RouterModule.forRoot(routes),
    FormsModule,
    HttpClientModule,
    BrowserAnimationsModule,
    MatTableModule,
    MatTabsModule,
    MatAutocompleteModule,
    MatFormFieldModule,
    MatInputModule,
    ReactiveFormsModule,
    MatDatepickerModule,
    MatNativeDateModule,
    NgChartsModule,
    NgxChartsModule,
  ],
  providers: [
    provideClientHydration(),
    MatDatepickerModule,
    MatNativeDateModule,
    DatePipe,
    {
      provide: HTTP_INTERCEPTORS,
      useClass: StockInvestmentService,
      multi: true
    },
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
