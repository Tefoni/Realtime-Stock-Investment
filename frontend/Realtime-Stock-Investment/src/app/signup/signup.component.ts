import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { StockInvestmentService } from '../services/stock-investment.service';

@Component({
  selector: 'app-signup',
  templateUrl: './signup.component.html',
  styleUrls: ['./signup.component.css'],
})
export class SignupComponent {
  name: string = '';
  email: string = '';
  password: string = '';
  repeatPassword: string = '';
  errorMessage: string = '';

  constructor(private router: Router, private service: StockInvestmentService) {}

  signup() {
    if(this.repeatPassword != this.password){
      this.service.showSnackBar("Şifreler uyuşmuyor",'error');
      return;
    }
    this.service.signup(this.email, this.password,this.name).subscribe(response => {
      if(response.isSuccessful){
        this.service.showSnackBar(response.message,'success');
        this.router.navigate(['/login']);
      }
      else{
        this.service.showSnackBar(response.message,'error');
      }
    });

  }

}
