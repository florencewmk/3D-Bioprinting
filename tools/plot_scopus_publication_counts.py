from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/publication-trends/scopus'
rows=list(csv.DictReader((OUT/'annual_counts_2000_2026.csv').open()))
labels=['Laser-assisted','Inkjet','Stereolithography','Extrusion'];colors=['#D08AB6','#B59BC8','#8FB79B','#7FA4C8']
years=np.array([int(r['Year']) for r in rows]);data={k:np.array([int(r[k]) for r in rows]) for k in labels}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'svg.fonttype':'none','text.color':'#3F345B','axes.labelcolor':'#3F345B','xtick.color':'#3F345B','ytick.color':'#3F345B'})
fig,ax=plt.subplots(figsize=(13,7.4));fig.subplots_adjust(left=.085,right=.98,top=.87,bottom=.27)
ax.axvspan(2025.5,2026.5,color='#DDE6F3',alpha=.5,zorder=0)
bottom=np.zeros(len(years))
for k,c in zip(labels,colors):
 bars=ax.bar(years,data[k],bottom=bottom,width=.6,color=c,label=k,zorder=3);bars[-1].set_hatch('///');bars[-1].set_edgecolor('#5c5470');bars[-1].set_linewidth(.4);bottom+=data[k]
ax.set_title('Publication trend per technique · Scopus',fontsize=18,pad=23)
ax.set_ylabel('Publications matching technique keywords per year',labelpad=10);ax.set_xlabel('Publication year',labelpad=10)
ax.set_xticks(years);ax.set_xticklabels([str(y)+('*' if y==2026 else '') for y in years],rotation=50,ha='right')
ax.set_xlim(1999.4,2026.6);ax.set_ylim(0,820);ax.set_yticks(np.arange(0,801,100));ax.grid(axis='y',color='#dedede',linewidth=.8);ax.set_axisbelow(True)
for x in ['top','right']:ax.spines[x].set_visible(False)
for x in ['bottom','left']:ax.spines[x].set_color('#cccccc')
ax.tick_params(length=0,pad=7)
inset=ax.inset_axes([.055,.44,.45,.49]);recent=years[-5:]
for k,c in zip(labels,colors):
 vals=data[k][-5:];inset.plot(recent[:-1],vals[:-1],color=c,marker='o',markersize=4,linewidth=2);inset.plot(recent[-2:],vals[-2:],color=c,marker='o',markersize=4,linewidth=2,linestyle='--')
inset.set_title('Last 5-year trend (2022–2026*)',fontsize=12,pad=9);inset.set_xticks(recent);inset.set_xticklabels(['2022','2023','2024','2025','2026*']);inset.set_ylim(0,460);inset.set_yticks([0,100,200,300,400]);inset.grid(axis='y',color='#e4e4e4');inset.tick_params(labelsize=9,length=0,pad=5)
for sp in inset.spines.values():sp.set_color('#cccccc')
fig.legend(*ax.get_legend_handles_labels(),loc='lower center',bbox_to_anchor=(.5,.10),ncol=4,frameon=False)
fig.text(.085,.064,'Source: Scopus (Elsevier) · English journal articles and reviews · Retrieved 27 October 2026',fontsize=9,color='#555555')
fig.text(.085,.037,'*2026 is year-to-date / indexed as of retrieval. Technique categories overlap; stacked totals are not unique papers.',fontsize=9,color='#555555')
for ext in ['png','svg','pdf']:fig.savefig(OUT/f'publication_trends_2000_2026.{ext}',dpi=250,facecolor='white')
