import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { StockInvestmentService } from '../services/stock-investment.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'],
})

export class LoginComponent {
  email: string = '';
  password: string = '';

  constructor(private router: Router, private service: StockInvestmentService) {}

  login(){
    this.service.login(this.email, this.password).subscribe(response => {
      if(response.isSuccessful){
        localStorage.setItem('token',response.token);
        this.service.setToken(response.token);
        this.router.navigate(['/main']);
      }
      else{
        this.service.showSnackBar(response.message,'error');
      }
    });
  }
 
  goToSignup() {
    // Use the Router to navigate to the signup page
    this.router.navigate(['/signup']);
  }
}
