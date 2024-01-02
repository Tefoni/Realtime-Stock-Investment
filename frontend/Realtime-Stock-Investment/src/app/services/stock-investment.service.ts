import { Injectable,Component,Inject,OnInit,PLATFORM_ID  } from '@angular/core';
import { HttpClient, HttpHeaders, HttpInterceptor, HttpHandler, HttpErrorResponse, HttpRequest, HttpEvent } from '@angular/common/http';
import { Observable, throwError  } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { MatSnackBar,MatSnackBarConfig } from '@angular/material/snack-bar';
import { isPlatformBrowser } from '@angular/common';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class StockInvestmentService implements HttpInterceptor  {
  private apiUrl = 'http://127.0.0.1:5000';
  private token = '';
  localStorageAvailable = false;

  constructor(private http: HttpClient, private snackBar: MatSnackBar, @Inject(PLATFORM_ID) private platformId: Object, private router: Router) {
    // Check if running in a browser environment before using localStorage
    if (isPlatformBrowser(this.platformId)) {
      this.localStorageAvailable = true;
      this.token = localStorage.getItem('token') ?? '';
    }
  }

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(request).pipe(
      catchError((error: HttpErrorResponse) => {
        if (error.status === 401) {
          // When 401 status is detected, redirect user to login page
          this.router.navigate(['/login']);
        }
        return throwError(error);
      })
    );
  }

  public login(email: string, password: string): Observable<any> {
    const body = {"email": email,"password": password};
    return this.http.post(`${this.apiUrl}/login`,body);
  }

  public signup(email: string, password: string, name: string): Observable<any> {
    const body = {"email": email,"password": password,"name": name};
    return this.http.post(`${this.apiUrl}/signUp`,body);
  }

  public getUserPortfolioIds(): Observable<any>{
    if(this.localStorageAvailable){
      const headers = new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`,
      });
      const options = {headers};
      
      return this.http.get(`${this.apiUrl}/userPortfolioIds`,options);
    }
    return new Observable<any>;
  }

  public getPortfolio(portfolioId: number): Observable<any>{
    if(this.localStorageAvailable){
      const headers = new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`,
      });
      const options = {headers};
      const body = {"portfolioId": portfolioId};
  
      return this.http.post(`${this.apiUrl}/portfolio`,body,options);
    }
    return new Observable<any>;
  }

  public getTransactions(portfolioId: number): Observable<any>{
    if(this.localStorageAvailable){
      const headers = new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`,
      });
      const options = {headers};
      const body = {"portfolioId": portfolioId};
  
      return this.http.post(`${this.apiUrl}/transactionHistory`,body,options);
    }
    return new Observable<any>;
  }

  public buyStock(portfolioId: number, symbol: string, amount: number, cost: number,date: Date): Observable<any>{
    if(this.localStorageAvailable){
      const headers = new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`,
      });
      const options = {headers};
      const body = {"portfolioId": portfolioId, "symbol": symbol, "amount": amount, "cost": cost, "date": date};
  
      return this.http.post(`${this.apiUrl}/buyStock`,body,options);
    }
    return new Observable<any>;   
  }

  public sellStock(portfolioId: number, symbol: string, amount: number, cost: number,date: Date): Observable<any>{
    if(this.localStorageAvailable){
      const headers = new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`,
      });
      const options = {headers};
      const body = {"portfolioId": portfolioId, "symbol": symbol, "amount": amount, "cost": cost, "date": date};
  
      return this.http.post(`${this.apiUrl}/sellStock`,body,options);
    }
    return new Observable<any>;   
  }

  public getStockSymbols(): Observable<any>{
    if(this.localStorageAvailable){
      const headers = new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`,
      });
      const options = {headers};  
      return this.http.get(`${this.apiUrl}/stockSymbols`,options);
    }
    return new Observable<any>;    
  }

  public showSnackBar(message: string, panelClass: string): void {
    const customStyle = panelClass == 'error' ? 'error-snackbar' : 'success-snackbar' 
    const config: MatSnackBarConfig = {
      duration: 1000,
      horizontalPosition: 'end',
      verticalPosition: 'top',
      panelClass: [panelClass,customStyle],
    };
    this.snackBar.open(message,'',config);
  }

  public setToken(newToken: string){
    this.token = newToken;
  }
}
