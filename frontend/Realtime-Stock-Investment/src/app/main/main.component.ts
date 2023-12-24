import { Component,Inject,OnInit,PLATFORM_ID } from '@angular/core';
import { Router } from '@angular/router';
import { StockInvestmentService } from '../services/stock-investment.service';
import { Observable, interval, map, startWith } from 'rxjs';
import { FormControl,FormGroup  } from '@angular/forms';
import { MatAutocompleteSelectedEvent } from '@angular/material/autocomplete';
import { DatePipe } from '@angular/common';


@Component({
  selector: 'app-main',
  templateUrl: './main.component.html',
  styleUrl: './main.component.css'
})

export class MainComponent {
  portfolioIds: number[] = [];
  currentPortfolioId: number = 0;
  currentSubTabIndex: number = 0;
  portfolioValues = {
    closedProfit: 0,
    dailyProfit: 0,
    marketValue: 0,
    openProfit: 0
  };
  stocks = [];
  transactions = [];
  portfolioColumns: string[] = ['symbol', 'amount', 'average_cost', 'lastPrice', 'marketValue', 'dailyStockProfit', 'dailyStockPercentageProfit', 'netStockProfit', 'netStockProfitPercentage'];
  transactionColumns: string[] = ['symbol', 'openDate','type', 'amount', 'openPrice', 'lastPrice', 'marketValue', 'dailyTransactionProfit', 'dailyTransactionPercentageProfit', 'netTransactionProfit', 'netTransactionProfitPercentage'];
  formControl = new FormControl('');
  filterOptions!: Observable<string[]>;
  stockNames!: string[];
  stockName!: string;
  form: FormGroup = new FormGroup({
    date: new FormControl(),
    amount: new FormControl(),
    price: new FormControl(),
  });

  constructor(private router: Router, private service: StockInvestmentService, @Inject(PLATFORM_ID) private platformId: Object, public datePipe: DatePipe)
  {
    this.service.getUserPortfolioIds().subscribe(response => {
      if(response.isSuccessful){
        this.portfolioIds = response.message;
      }
      else{
        this.service.showSnackBar(response.message,'error');
      }
    });
  }

  ngOnInit()
  { 
    this.service.getStockSymbols().subscribe(response => {
      if(response.isSuccessful){
        this.stockNames = response.message;
        this.filterOptions = this.formControl.valueChanges.pipe(
          startWith(''),map(value => this.filter(value || ''))
        )
      }
      else{
        this.service.showSnackBar(response.message,'error');
      }
    });
    interval(1000).subscribe(() => {
      if(this.currentPortfolioId != 0){
        this.service.getPortfolio(this.currentPortfolioId).subscribe(response => {
          if(response.isSuccessful){
            this.stocks = response.stocks;
            this.portfolioValues = response;
          }
          else{
            this.service.showSnackBar(response.message,'error');
          }
        });
      }

      if(this.currentSubTabIndex == 1){ // Transactions
        this.service.getTransactions(this.currentPortfolioId).subscribe(response => {
          if(response.isSuccessful){
            this.transactions = response.message;
          }
          else{
            this.service.showSnackBar(response.message,'error');
          }
        });
      }
    });
  }

  private filter(value:string) : string[] {
    const searchValue = value.toLocaleLowerCase();
    return this.stockNames.filter(option => option.toLocaleLowerCase().includes(searchValue));
  }

  loadTableData(portfolioId:any)
  { 
    this.currentSubTabIndex = 0;
    this.formControl.setValue(null);
    this.stockName = '';
    this.form.setValue({date: null,amount: null,price: null});
    this.currentPortfolioId = this.portfolioIds[portfolioId];
    this.service.getPortfolio(this.currentPortfolioId).subscribe(response => {
      if(response.isSuccessful){
        this.stocks = response.stocks;
        this.portfolioValues = response;
      }
      else{
        this.service.showSnackBar(response.message,'error');
      }
    });
  }

  onTabChange(event: any)
  {
    this.currentSubTabIndex = event;
    if(this.currentSubTabIndex == 1){ // Transactions
      this.service.getTransactions(this.currentPortfolioId).subscribe(response => {
        if(response.isSuccessful){
          this.transactions = response.message;
        }
        else{
          this.service.showSnackBar(response.message,'error');
        }
      });
    }
    else if(this.currentSubTabIndex == 2){
      // İstatistik
    }
  }

  changeRowColor(value: number)
  {
    if(value == 0)
      return 'bold-text';
    return value > 0 ? 'positive-color' : 'negative-color';
  }

  onStockSelected(event: MatAutocompleteSelectedEvent): void{
    const selectedStockName = event.option.viewValue;
    this.stockName = selectedStockName;
    this.formControl.setValue(selectedStockName);
    this.form.setValue({date: null,amount: null,price: null});
  }

  onBuyClick(){
    this.service.buyStock(this.currentPortfolioId, this.stockName, this.form.value.amount, this.form.value.price, this.form.value.date).subscribe(response => {
      if(response.isSuccessful){
        this.service.showSnackBar(response.message,'success');
      }
      else{
        this.service.showSnackBar(response.message,'error');
      }
    });
  }

  onSellClick(){
    this.service.sellStock(this.currentPortfolioId, this.stockName, this.form.value.amount, this.form.value.price, this.form.value.date).subscribe(response => {
      if(response.isSuccessful){
        this.service.showSnackBar(response.message,'success');
      }
      else{
        this.service.showSnackBar(response.message,'error');
      }
    });
  }

  async onBlur(){
    await new Promise(resolve => setTimeout(resolve, 150));
    if(this.stockName != this.formControl.value && !this.stockNames.includes(this.formControl.value ?? ""))
      if(this.formControl.value == ''){
        this.stockName = '';
        this.formControl.setValue(null);
        this.form.setValue({date: null,amount: null,price: null});
      }
      else
        this.formControl.setValue(this.stockName);
  }
}
