def write_cell_values(cell_values, taxon): pass


# if SeasonFlg = False Then       'not pegalic species, so Annual distribution
#     produceGridFile(pathA & "S" & taxKey & ".csv", cell_values)
#     frmSpeDistBuild.prgProgressBar.PerformStep() '9
#     taxaDistribution.WriteAscii(pathA, cell_values, taxKey)
# Else 'Pelagic spp
#     if Season = 0 Then      'annual distribution
#         produceGridFile(pathA & "S" & taxKey & ".csv", cell_values)
#         frmSpeDistBuild.prgProgressBar.PerformStep() '9
#         taxaDistribution.WriteAscii(pathA, cell_values, taxKey)

#     Else        'Seasonal distribution
#         if Season = 1 Then      'Summer distribution
#             if Equator = True Then          'Distribution across equator
#                 if TwoPop = True Then
#                     if NSHem = 1 Then   'Northern hemisphere
#                         'Store the value in another array for later use
#                         NHemCellVal = cell_values
#                     Else        'Southern hemisphere
#                         'Combine the abundance values in the N and S hemisphere
#                         cell_values = CombineNSHem(cell_values, NHemCellVal)
#                         ReDim NHemCellVal(0)
#                         OutSeasonPath = pathSummer & "S" & taxKey & ".csv"
#                         produceGridFile(OutSeasonPath, cell_values) 'no ERROR HANDLE!!!
#                         frmSpeDistBuild.prgProgressBar.PerformStep() '9
#                         taxaDistribution.WriteAscii(pathSummer, cell_values, taxKey)
#                     End if
#                 Else        'Not Equatorial species
#                     OutSeasonPath = pathSummer & "S" & taxKey & ".csv"
#                     produceGridFile(OutSeasonPath, cell_values) 'no ERROR HANDLE!!!
#                     frmSpeDistBuild.prgProgressBar.PerformStep() '9
#                     taxaDistribution.WriteAscii(pathSummer, cell_values, taxKey)
#                 End if
#             Else
#                 OutSeasonPath = pathSummer & "S" & taxKey & ".csv"
#                 produceGridFile(OutSeasonPath, cell_values) 'no ERROR HANDLE!!!
#                 frmSpeDistBuild.prgProgressBar.PerformStep() '9
#                 taxaDistribution.WriteAscii(pathSummer, cell_values, taxKey)
#             End if
#         Else    'Winter Distribution
#             if Equator = True Then          'Distribution across equator
#                 if TwoPop = True Then
#                     if NSHem = 1 Then   'Northern hemisphere
#                         'Store the value in another array for later use
#                         NHemCellVal = cell_values
#                     Else        'Southern hemisphere
#                         'Combine the abundance values in the N and S hemisphere
#                         cell_values = CombineNSHem(cell_values, NHemCellVal)
#                         ReDim NHemCellVal(0)
#                         OutSeasonPath = pathWinter & "S" & taxKey & ".csv"
#                         produceGridFile(OutSeasonPath, cell_values) 'no ERROR HANDLE!!!
#                         frmSpeDistBuild.prgProgressBar.PerformStep() '9
#                         taxaDistribution.WriteAscii(pathWinter, cell_values, taxKey)
#                     End if
#                 Else        'Not Equatorial species
#                     OutSeasonPath = pathWinter & "S" & taxKey & ".csv"
#                     produceGridFile(OutSeasonPath, cell_values) 'no ERROR HANDLE!!!
#                     frmSpeDistBuild.prgProgressBar.PerformStep() '9
#                     taxaDistribution.WriteAscii(pathWinter, cell_values, taxKey)
#                 End if
#             Else
#                 OutSeasonPath = pathWinter & "S" & taxKey & ".csv"
#                 produceGridFile(OutSeasonPath, cell_values) 'no ERROR HANDLE!!!
#                 frmSpeDistBuild.prgProgressBar.PerformStep() '9
#                 taxaDistribution.WriteAscii(pathWinter, cell_values, taxKey)
#             End if
#         End if
#     End if


# End if
