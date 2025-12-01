# Component Selection Rationale

**Experiment:** 3-Photon GHZ State Generator via Sequential Entanglement Swapping

**Timestamp:** 20251125_152732

**Description:** Generates genuine 3-photon GHZ states by performing sequential Bell state measurements on shared photons from three independent SPDC sources to create tripartite entanglement through quantum swapping

---

## 1. Pump Laser 1

405nm pump for first SPDC source generating Bell pair (A1,A2)

## 2. Pump Laser 2

405nm pump for second SPDC source generating Bell pair (B1,B2)

## 3. Pump Laser 3

405nm pump for third SPDC source generating Bell pair (C1,C2)

## 4. BBO Crystal 1

Type-II SPDC crystal creating entangled photon pair A1-A2

## 5. BBO Crystal 2

Type-II SPDC crystal creating entangled photon pair B1-B2

## 6. BBO Crystal 3

Type-II SPDC crystal creating entangled photon pair C1-C2

## 7. Collection Lens 1

Collects and focuses SPDC photons from first crystal

## 8. Collection Lens 2

Collects and focuses SPDC photons from second crystal

## 9. Collection Lens 3

Collects and focuses SPDC photons from third crystal

## 10. Bandpass Filter 1

Filters 810nm down-converted photons, blocks pump light

## 11. Bandpass Filter 2

Filters 810nm down-converted photons, blocks pump light

## 12. Bandpass Filter 3

Filters 810nm down-converted photons, blocks pump light

## 13. BS1

Separates photon pair A1-A2 from first SPDC source

## 14. BS2

Separates photon pair B1-B2 from second SPDC source

## 15. BS3

Separates photon pair C1-C2 from third SPDC source

## 16. Mirror A1

Routes photon A1 to final GHZ detection path

## 17. Mirror A2

Routes photon A2 to first Bell measurement station

## 18. Mirror B1

Routes photon B1 to first Bell measurement station

## 19. Mirror B2

Routes photon B2 to second Bell measurement station

## 20. Mirror C1

Routes photon C1 to second Bell measurement station

## 21. Mirror C2

Routes photon C2 to final GHZ detection path

## 22. Bell PBS 1

Performs Bell state measurement on photons A2 and B1 for first swapping operation

## 23. Bell PBS 2

Performs Bell state measurement on photons B2 and C1 for second swapping operation

## 24. HWP 1

Rotates polarization for optimal Bell state measurement at first PBS

## 25. HWP 2

Rotates polarization for optimal Bell state measurement at second PBS

## 26. Bell Detector 1A

Detects one output of first Bell state measurement

## 27. Bell Detector 1B

Detects other output of first Bell state measurement

## 28. Bell Detector 2A

Detects one output of second Bell state measurement

## 29. Bell Detector 2B

Detects other output of second Bell state measurement

## 30. Mirror GHZ A

Routes final GHZ photon A1 to analysis station

## 31. Mirror GHZ B

Routes final GHZ photon B2 to analysis station

## 32. Mirror GHZ C

Routes final GHZ photon C2 to analysis station

## 33. Polarizer A

Analyzes polarization of final GHZ photon A1

## 34. Polarizer B

Analyzes polarization of final GHZ photon B2

## 35. Polarizer C

Analyzes polarization of final GHZ photon C2

## 36. GHZ Detector A

Measures final GHZ state photon A1

## 37. GHZ Detector B

Measures final GHZ state photon B2

## 38. GHZ Detector C

Measures final GHZ state photon C2

## 39. Swapping Controller

Processes Bell measurement outcomes and gates GHZ detection events to herald successful 3-photon entanglement generation

