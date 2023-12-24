import { TestBed } from '@angular/core/testing';
import { StockInvestmentService } from './stock-investment.service';

describe('StockInvestmentService', () => {
  let service: StockInvestmentService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(StockInvestmentService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
