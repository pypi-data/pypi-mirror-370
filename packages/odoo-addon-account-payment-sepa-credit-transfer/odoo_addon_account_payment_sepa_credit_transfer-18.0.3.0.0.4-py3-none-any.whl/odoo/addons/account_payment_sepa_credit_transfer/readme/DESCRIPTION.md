Module to export payment orders in ISO 20022 XML file format.

[ISO 20022](https://www.iso20022.org/) is the new international standard
for bank XML files. This module implements SEPA Credit Transfer (SCT),
more specifically ISO 20022 PAIN (PAyment INitiation) versions
001.001.03 and 001.001.09. It follows the [SEPA credit transfer
implementation
guidelines](https://www.europeanpaymentscouncil.eu/what-we-do/epc-payment-schemes/sepa-credit-transfer/sepa-credit-transfer-rulebook-and)
of the [European Payments
Council](https://www.europeanpaymentscouncil.eu).

This module also supports PAIN version 001.003.03 which is used in
Germany. You can read more about this in german on
[ebics.de](https://www.ebics.de/).

Moreover, this module supports:

- SEPA **instant** credit transfer,
- non-SEPA credit transfer files, which can be used for wire transfer in
  currencies other then euro and/or to countries outside the [SEPA
  zone](https://en.wikipedia.org/wiki/Single_Euro_Payments_Area).
