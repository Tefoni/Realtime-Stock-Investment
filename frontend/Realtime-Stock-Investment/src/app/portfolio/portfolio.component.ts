import { Component, EventEmitter, Output } from '@angular/core';
import { Router } from '@angular/router';
import { StockInvestmentService } from '../services/stock-investment.service';
import { FormControl } from '@angular/forms';
import { Observable } from 'rxjs';
import { map, startWith } from 'rxjs/operators';

@Component({
  selector: 'app-portfolio',
  templateUrl: './portfolio.component.html',
  styleUrl: './portfolio.component.css'
})
export class PortfolioComponent {

  constructor(private router: Router, private service: StockInvestmentService)
  {
  }

  
  portfolioIds: number[] =[];
  currentPortfolioId: number = this.portfolioIds[0];
  stockNames!: string[];
  filterOptions!: Observable<string[]>;
  formControl = new FormControl('');

  ngOnInit(){
    this.service.getUserPortfolioIds().subscribe(response => {
      if(response.isSuccessful){
        this.portfolioIds = response.message;
        this.currentPortfolioId = this.portfolioIds[0];
        //this.setProfitHistoryChart();
        //this.setStockDistribution();
      }
      else{
        this.service.showSnackBar(response.message,'error');
      }
    });

    this.service.getStockSymbols().subscribe(response => {
      if(response.isSuccessful){
        this.stockNames = response.message;
        this.filterOptions = this.formControl.valueChanges.pipe(
          startWith(''),map((value: any) => this.filter(value || ''))
        )
      }
      else{
        this.service.showSnackBar(response.message,'error');
      }
    });
  }
  addTab() {
    this.service.addPortfolio().subscribe(response => {
     if(response.isSuccessful){
       this.service.getUserPortfolioIds().subscribe(response => {
        if(response.isSuccessful){
          this.portfolioIds = response.message;
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
}
