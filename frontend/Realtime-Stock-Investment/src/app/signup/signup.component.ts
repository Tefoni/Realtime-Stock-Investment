import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { StockInvestmentService } from '../services/stock-investment.service';
import { FormControl, FormGroup, Validators } from '@angular/forms';

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
    if(this.name == ''){
      this.service.showSnackBar("Lütfen isim giriniz.",'error');
      return;
    }
    if(!( this.email.includes('@') && this.email.includes('.') && this.email.length >= 5) ){
      this.service.showSnackBar("Geçerli bir email giriniz.",'error');
      return;
    }
    if(this.repeatPassword != this.password){
      this.service.showSnackBar("Şifreler uyuşmuyor",'error');
      return;
    }
    if(this.password.length < 8){
      this.service.showSnackBar("Şifre en az 8 karakterden oluşmalıdır.",'error');
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
  goToLogin() {
    this.router.navigate(['/login']);
  }

}
