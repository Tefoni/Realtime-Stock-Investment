import { Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { Observable, Subscription, interval } from 'rxjs';
import { map, startWith } from 'rxjs/operators';
import { StockInvestmentService } from '../services/stock-investment.service';

@Component({
  selector: 'app-watch-list',
  templateUrl: './watch-list.component.html',
  styleUrl: './watch-list.component.css'
})
export class WatchListComponent {
  private updateSubscription!: Subscription;
  marketData = [
    { market: 'GARAN', change: 3.91, last: 102.2, high: 103.40, low: 98.2, open: 98.45, volume: '1316220535', time: '17:45:05' },
    { market: 'AKBNK', change: 2.78, last: 61.15, high: 61.60, low: 59.2, open: 59.45, volume: '3852291832', time: '17:45:05' },
    { market: 'TUPRS', change: -0.49, last: 161.60, high: 163.00, low: 159.70, open: 162.30, volume: '3971625305', time: '17:45:05' },
    { market: 'SAHOL', change: 1.45, last: 90.95, high: 91.00, low: 89.45, open: 89.65, volume: '1683140743', time: '17:45:05' },
  ];
  marketNames: string[] = [];

  searchControl = new FormControl();
  filteredOptions: string[] = [];
  allOptions: string[] = ['GARAN', 'AKBNK', 'ISCTR', 'YKBNK', 'VAKBN', 'HALKB', 'TUPRS', 'EREGL', 'PETKM', 'SAHOL'];

  constructor(private service: StockInvestmentService) { }


  ngOnInit(){
    this.service.getStockSymbols().subscribe(response => {
      if(response.isSuccessful){
        this.allOptions = response.message;
        this.allOptions = response.message.map((option: string) => option.replace('.IS', ''));
        this.filteredOptions = this.allOptions;
      }
      else{
        this.service.showSnackBar(response.message,'error');
      }
    });
    this.searchControl.valueChanges.pipe(
      startWith(''),
      map(value => this._filter(value))
    ).subscribe(filtered => this.filteredOptions = filtered);


    this.service.getMarketStocks(this.marketNames).subscribe(response => {
      if(response.isSuccessful){
        this.marketData = response.message;
      }
      else{
        this.service.showSnackBar(response.message,'error');
      }
    });

    this.updateSubscription = interval(5000).subscribe(() => {
      this.service.getMarketStocks(this.marketNames).subscribe(response => {
        if(response.isSuccessful){
          this.marketData = response.message;
        }
        else{
          this.service.showSnackBar(response.message,'error');
        }
      });
    });

  }

  ngOnDestroy(){
    if (this.updateSubscription) {
      this.updateSubscription.unsubscribe();
    }
  }

  private _filter(value: string): string[] {
    const filterValue = value.toLowerCase();
    return this.allOptions.filter(option => option.toLowerCase().includes(filterValue));
  }

  onOptionSelected(event: any): void {
    const selectedMarket = event.option.value;
    this.marketNames.push(selectedMarket + ".IS");

    this.service.getMarketStocks(this.marketNames).subscribe(response => {
      if(response.isSuccessful){
        this.marketData = response.message;
      }
      else{
        this.service.showSnackBar(response.message,'error');
      }
    });
  }

  deleteRow(index: number): void {
    this.marketNames.splice(index,1);
    this.service.getMarketStocks(this.marketNames).subscribe(response => {
      if(response.isSuccessful){
        this.marketData = response.message;
      }
      else{
        this.service.showSnackBar(response.message,'error');
      }
    });
  }
}
