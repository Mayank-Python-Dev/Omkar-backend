import matplotlib.pyplot as plt, base64
from io import BytesIO

def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer,format="png")
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph


def get_plot(years_list,gala_free_area_list,get_year,colors):
    plt.switch_backend("AGG")
    plt.figure(figsize = (10,5))
    plt.plot(years_list,gala_free_area_list)
    plt.tight_layout()
    # ax = fig.add_axes([0,0,1,1])
    # ax.bar(years_list,gala_free_area_list,color = colors)
    # ax.set_title(f'Gala Free Area Size ({get_year})')
    # plt.xticks(rotation=75)
    # ax.bar_label(ax.containers[0], label_type='center', color='black',rotation=90, fontsize=9, padding=1)
    # plt.grid(color='grey', linewidth=0.2, axis='both',linestyle='-',)
    graph = get_graph()
    return graph
    pass