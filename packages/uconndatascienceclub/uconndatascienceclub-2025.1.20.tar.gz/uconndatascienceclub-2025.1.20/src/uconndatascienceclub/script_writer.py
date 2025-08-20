import nbformat as nbf

all_scripts = dict() #nested dictionary; contains dates (key), points to 2nd dictionary (value) containing collection of scripts from that date

# FORMAT:
#
# all_scripts['date'] = {'nb': [True/False] (True if file is .ipynb, false if file is .py)
#                        'filename': 'file_name.ipynb' or 'file_name.py' (name can be anything)
#                        1: [nbformat list containing all cells]; if python file, will need to use os library
#                        ...
#                        n: [nbformat list containing all cells]; if a workshop requires multiple files, each file
#                           can be given their own integer key. Most of the time, only one file is necessary however.
#                           I'm realizing now that filename would be the same for all notebooks, so that would have
#                           to be fixed
#                        }

all_scripts['1/30/2025'] = {'nb': True,
                            'filename': 'advanced_data_visualization.ipynb',
                            1: [
        nbf.v4.new_code_cell("""
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import uconndatascienceclub as ucdsc
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
"""),
        
        nbf.v4.new_code_cell("""
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)
y3 = np.tan(x)
y4 = np.exp(-x)

plt.figure(figsize=(10, 8))

plt.subplot(2, 2, 1) 
plt.plot(x, y1, label='sin(x)')
plt.title('sin(x)')
plt.legend()

plt.subplot(2, 2, 2)  
plt.plot(x, y2, label='cos(x)', color='orange')
plt.title('cos(x)')
plt.legend()

plt.subplot(2, 2, 3) 
plt.plot(x, y3, label='tan(x)', color='orange')
plt.title('tan(x)')
plt.legend(['test'])

plt.subplot(2, 2, 4)  
plt.plot(x, y4, label='exp(-x)', color='red')
plt.title('exp(-x)')
plt.legend()

plt.tight_layout()
plt.show()
"""),
        
        nbf.v4.new_code_cell("""
fig, ax = plt.subplots(1, 1)
x = np.linspace(0, 10, 100)
line, = ax.plot(x, np.sin(x), color='blue')

ax.set_xlim(0, 10)
ax.set_ylim(-1.5, 1.5)
ax.set_title("Animating a Sine Wave")
ax.set_xlabel("X")
ax.set_ylabel("Amplitude")

def update(frame):
    line.set_ydata(np.sin(x + frame * 0.1)) 
    return line,

ani = animation.FuncAnimation(fig, update, frames=100, interval=50, blit=True)
ani.save("sine_wave.gif", writer=animation.PillowWriter(fps=20))

plt.show()
"""),
        
        nbf.v4.new_code_cell("""
df = ucdsc.Data('fires').dataframe()
category_counts = df['day'].value_counts()

categories = category_counts.index.tolist()
final_heights = category_counts.values

fig, ax = plt.subplots(figsize=(8, 6))
x = np.arange(len(categories))  
current_heights = np.zeros(len(categories))  
growth_rates = final_heights / 50 
bars = ax.bar(x, current_heights, tick_label=categories, color="royalblue")

ax.set_ylim(0, max(final_heights) * 1.1)
ax.set_title("Wildfire Counts by Day of Week", fontsize=14)
ax.set_xlabel("DOW")
ax.set_ylabel("Count")

def update(frame):
    for i, bar in enumerate(bars):
        if current_heights[i] < final_heights[i]:  # Grow until target
            current_heights[i] += growth_rates[i]
            bar.set_height(current_heights[i])
    return bars

ani = animation.FuncAnimation(fig, update, frames=50, interval=50, blit=False)

ani.save("fire_growth.gif", writer=animation.PillowWriter(fps=20))

plt.show()
"""),
        
        nbf.v4.new_code_cell("""
df = ucdsc.Data('population').dataframe()

fig = px.scatter(df, x="Longitude", y="Latitude", size="Population", hover_name="City", text="City",
                 color="Population", 
                 title="Interactive Population Map of Major US Cities")

fig.update_traces(textposition="top center", marker=dict(opacity=0.8))
fig.show()
"""),
        
        nbf.v4.new_code_cell("""
df = ucdsc.Data('temperatures').dataframe()
df = df.sort_values("Year")

fig = go.Figure()

fig.add_trace(go.Scatter(x=df["Year"], y=df["Mean"], mode="lines",
                         name="Global Mean Temperature Anomaly"))

fig.update_layout(title="Global Monthly Mean Temperature Anomaly (1880-Present)",
                  xaxis_title="Year", yaxis_title="Temperature Anomaly (°C)",
                  )

fig.show()
""")
    ]}
all_scripts['2/27/2025'] = {'nb': True,
                            'filename': 'pca.ipynb',
                            1: [
    nbf.v4.new_code_cell("""
import uconndatascienceclub as ucdsc
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import numpy as np
"""),

    nbf.v4.new_code_cell("""
df = ucdsc.Data().generate(dim=20, size=200, mean=[0, 200], sd=[10, 100], distributions=['normal', 'exponential'])
df.head()
"""),

    nbf.v4.new_code_cell("""
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df)

pca = PCA(n_components=10) 
X_pca = pca.fit_transform(X_scaled)

explained_variance = pca.explained_variance_ratio_
X_pca.shape
"""),

    nbf.v4.new_code_cell("""
plt.figure(figsize=(8, 6))
plt.scatter(X_pca[:, 0], X_pca[:, 1], alpha=0.5, c='blue', edgecolors='k')
plt.xlabel(f"PC1 ({explained_variance[0]*100:.2f}% Variance)")
plt.ylabel(f"PC2 ({explained_variance[1]*100:.2f}% Variance)")
plt.title("PCA Projection of Dataset (First 2 Components)")
plt.axhline(0, color='gray', linestyle='--', alpha=0.5)
plt.axvline(0, color='gray', linestyle='--', alpha=0.5)
plt.show()
"""),

    nbf.v4.new_code_cell("""
X = ucdsc.Data('automobile').dataframe()
X.head()
"""),

    nbf.v4.new_code_cell("""
X.replace('?', np.nan, inplace=True)
X.dropna(inplace=True)

x = X[["highway-mpg", "engine-size", "horsepower", "curb-weight"]]
y = X['price']
x.shape
"""),

    nbf.v4.new_code_cell("""
scaler = StandardScaler()
X_scaled = scaler.fit_transform(x)

pca = PCA(n_components=3)  
X_pca = pca.fit_transform(X_scaled)

explained_variance = pca.explained_variance_ratio_
explained_variance
"""),

    nbf.v4.new_code_cell("""
plt.bar(x=['pca1', 'pca2', 'pca3'], height=explained_variance)
plt.show()
""")
]}
all_scripts['3/6/2025'] = {'nb': True,
                           'filename': 'audio_model.ipynb',
                           1: [
    nbf.v4.new_code_cell("""
import pandas as pd
import librosa
import numpy as np
import matplotlib.pyplot as plt
"""),

    nbf.v4.new_code_cell("""
data, sample_rate = librosa.load('sample_happy_audio.wav') #replace with audio file name

librosa.display.waveshow(data, sr=sample_rate, alpha=0.8)
plt.title("Original Audio Waveform")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.tight_layout()
plt.show()
"""),

    nbf.v4.new_code_cell("""
mel = []
mfcc = []
rms = []
zero = []

mel.append(np.mean(librosa.feature.melspectrogram(y=data, sr=sample_rate).T, axis=0))
mfcc.append(np.mean(librosa.feature.mfcc(y=data, sr=sample_rate, n_mfcc=16).T, axis=0))
rms.append(librosa.feature.rms(y=data).flatten())
zero.append(librosa.feature.zero_crossing_rate(y=data).flatten())
"""),

    nbf.v4.new_code_cell("""
# Adds random noise to the audio signal
def noise(data, noise_level=0.02):
    noise_amp = noise_level * np.amax(data)
    return data + noise_amp * np.random.normal(size=data.shape)

# Alters the speed (time stretch) of the audio without changing its pitch
def stretch(data, rate_range=(0.8, 1.2)):
    rate = np.random.uniform(*rate_range)
    return librosa.effects.time_stretch(data, rate=rate)

# Shifts the audio data by rolling the waveform along the time axis
def shift(data, max_shift_fraction=0.2):
    shift_range = int(np.random.uniform(-max_shift_fraction, max_shift_fraction) * len(data))
    return np.roll(data, shift_range)

# Changes the pitch of the audio signal without altering the speed
def pitch(data, sampling_rate, pitch_range=(-2, 2)):
    pitch_factor = np.random.uniform(*pitch_range)
    return librosa.effects.pitch_shift(data, sr=sampling_rate, n_steps=pitch_factor)

# Randomly amplify or attenuate the signal to simulate varying microphone volumes
def volume_scale(data, scale_range=(0.8, 1.2)):
    scale = np.random.uniform(*scale_range)
    return data * scale
"""),

    nbf.v4.new_code_cell("""
noise_data = noise(data)
mel.append(np.mean(librosa.feature.melspectrogram(y=noise_data, sr=sample_rate).T, axis=0))
mfcc.append(np.mean(librosa.feature.mfcc(y=noise_data, sr=sample_rate, n_mfcc=16).T, axis=0))
rms.append(librosa.feature.rms(y=noise_data).flatten())
zero.append(librosa.feature.zero_crossing_rate(y=noise_data).flatten())

stretch_data = stretch(data)
mel.append(np.mean(librosa.feature.melspectrogram(y=stretch_data, sr=sample_rate).T, axis=0))
mfcc.append(np.mean(librosa.feature.mfcc(y=stretch_data, sr=sample_rate, n_mfcc=16).T, axis=0))
rms.append(librosa.feature.rms(y=stretch_data).flatten())
zero.append(librosa.feature.zero_crossing_rate(y=stretch_data).flatten())

shift_data = shift(data)
mel.append(np.mean(librosa.feature.melspectrogram(y=shift_data, sr=sample_rate).T, axis=0))
mfcc.append(np.mean(librosa.feature.mfcc(y=shift_data, sr=sample_rate, n_mfcc=16).T, axis=0))
rms.append(librosa.feature.rms(y=shift_data).flatten())
zero.append(librosa.feature.zero_crossing_rate(y=shift_data).flatten())

pitch_data = pitch(data, sample_rate)
mel.append(np.mean(librosa.feature.melspectrogram(y=pitch_data, sr=sample_rate).T, axis=0))
mfcc.append(np.mean(librosa.feature.mfcc(y=pitch_data, sr=sample_rate, n_mfcc=16).T, axis=0))
rms.append(librosa.feature.rms(y=pitch_data).flatten())
zero.append(librosa.feature.zero_crossing_rate(y=pitch_data).flatten())

volume_data = volume_scale(data)
mel.append(np.mean(librosa.feature.melspectrogram(y=volume_data, sr=sample_rate).T, axis=0))
mfcc.append(np.mean(librosa.feature.mfcc(y=volume_data, sr=sample_rate, n_mfcc=16).T, axis=0))
rms.append(librosa.feature.rms(y=volume_data).flatten())
zero.append(librosa.feature.zero_crossing_rate(y=volume_data).flatten())
"""),

    nbf.v4.new_code_cell("""
df1 = pd.DataFrame(mel)
df1.columns = ['mel' + str(i) for i in range(1, len(df1.columns) + 1)]

df2 = pd.DataFrame(mfcc)
df2.columns = ['mfcc' + str(i) for i in range(1, len(df2.columns) + 1)]

df3 = pd.DataFrame(rms)
df3.columns = ['rms' + str(i) for i in range(1, len(df3.columns) + 1)]

df4 = pd.DataFrame(zero)
df4.columns = ['zero' + str(i) for i in range(1, len(df4.columns) + 1)]

df = pd.concat([df1, df2, df3, df4], axis=1)
df
"""),

    nbf.v4.new_code_cell("df.fillna(0, inplace=True)"),

    nbf.v4.new_code_cell("""
df['emotion'] = ['happy', 'sad', 'fear', 'angry', 'surprised', 'neutral']
df
"""),

    nbf.v4.new_code_cell("""
from sklearn.preprocessing import OneHotEncoder, StandardScaler

X = df.drop(columns=['emotion'])
scaler = StandardScaler()
X = scaler.fit_transform(X)

y = df['emotion']
encoder = OneHotEncoder()

y = encoder.fit_transform(y.to_numpy().reshape(-1, 1))
y = y.toarray()
encoder.categories_
"""),

    nbf.v4.new_code_cell("""
# NOTE: Everything in this cell and the cells below will most likely not work properly with the sample data created before. They are for pure observation purposes.
import torch
import torch.nn as nn
import torch.nn.functional as F

class CNNEmotionClassifier(nn.Module):
    def __init__(self, num_classes=6):
        super(CNNEmotionClassifier, self).__init__()

        self.conv1 = nn.Conv1d(1, 64, 5, padding=2)
        self.conv2 = nn.Conv1d(64, 128, 5, padding=2)
        self.conv3 = nn.Conv1d(128, 256, 5, padding=2)
        self.conv4 = nn.Conv1d(256, 512, 3, padding=1)

        self.fc1 = None
        self.fc2 = nn.Linear(512, 256)
        self.output = nn.Linear(256, num_classes)

    def forward(self, x):
        x = x.view(x.size(0), 1, -1)  
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        x = F.relu(self.conv4(x))

        x = x.view(x.size(0), -1)
        if self.fc1 is None:
            self.fc1 = nn.Linear(x.size(1), 512)
            self.fc1.to(x.device) 

        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.output(x)
        return x
"""),

    nbf.v4.new_code_cell('''
X_train = torch.tensor(X, dtype=torch.float32)
y_train = torch.tensor(y, dtype=torch.long)
    '''),

    nbf.v4.new_code_cell('''
                         
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

input_size = X_train.shape[1]  
batch_size = 32
num_epochs = 12
learning_rate = 0.001

dataset = TensorDataset(X_train, y_train)
data_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, drop_last=True)

model = CNNEmotionClassifier(input_size)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=learning_rate, weight_decay=1e-4)

# Training loop

for epoch in range(num_epochs):
    model.train() 
    running_loss = 0.0
    
    for batch_idx, (X_batch, y_batch) in enumerate(data_loader):
        y_batch = torch.argmax(y_batch, dim=1)

        X_batch = X_batch.float()
        y_batch = y_batch.long()

        optimizer.zero_grad()
        outputs = model(X_batch)
        loss = criterion(outputs, y_batch)
        
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item()
    
    avg_loss = running_loss / len(data_loader)
    print(f"Epoch [{epoch + 1}/{num_epochs}], Loss: {avg_loss:.4f}")
'''),

    nbf.v4.new_code_cell('''
                         #Testing
model.eval()
X_test = None #replace with real test data
y_test = None #replace with real test data

test_dataset = TensorDataset(X_test, y_test)
test_data_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

correct_predictions = 0
total_predictions = 0
running_loss = 0.0

with torch.no_grad():  
    for X_batch, y_batch in test_data_loader:
        X_batch = X_batch.float()
        y_batch = torch.argmax(y_batch, dim=1)  
        
        outputs = model(X_batch)
        loss = criterion(outputs, y_batch)
        
        running_loss += loss.item()
        
        _, predicted = torch.max(outputs, 1)  
        total_predictions += y_batch.size(0)
        correct_predictions += (predicted == y_batch).sum().item()

avg_loss = running_loss / len(test_data_loader)
accuracy = (correct_predictions / total_predictions) * 100''')

]}
all_scripts['4/3/2025'] = {'nb': True,
                           'filename': 'decision_tree.ipynb',
                           1: [
    nbf.v4.new_code_cell("from sklearn.datasets import load_iris\niris = load_iris()"),
    
    nbf.v4.new_code_cell(
        "import pandas as pd\n"
        "df = pd.DataFrame(iris.data, columns=iris.feature_names)\n"
        "df['target'] = iris.target\n"
        "df.head()"
    ),
    
    nbf.v4.new_code_cell(
        "from sklearn.tree import DecisionTreeClassifier\n"
        "model = DecisionTreeClassifier(max_depth=5, criterion='gini', min_samples_leaf=2)"
    ),
    
    nbf.v4.new_code_cell(
        "from sklearn.model_selection import train_test_split\n"
        "x_train, x_test, y_train, y_test = train_test_split(iris.data, iris.target, test_size=0.2)\n"
        "model.fit(x_train, y_train)"
    ),
    
    nbf.v4.new_code_cell(
        "from sklearn.tree import export_text\n"
        "text_representation = export_text(model, feature_names=iris['feature_names'])\n"
        "print(text_representation)"
    ),
    
    nbf.v4.new_code_cell(
        "from sklearn.metrics import accuracy_score\n"
        "y_pred = model.predict(x_test)\n"
        "accuracy_score(y_test, y_pred)"
    ),
    
    nbf.v4.new_code_cell(
        "from sklearn.tree import export_graphviz\n"
        "# Export as dot file\n"
        "export_graphviz(model, out_file='tree.dot',\n"
        "                feature_names = iris.feature_names,\n"
        "                class_names = iris.target_names,\n"
        "                rounded = True, proportion = False,\n"
        "                precision = 2, filled = True)"
    ),
    
    nbf.v4.new_code_cell(
        "from subprocess import call\n"
        "call(['dot', '-Tpng', 'tree.dot', '-o', 'tree.png', '-Gdpi=600'])"
    ),
    
    nbf.v4.new_code_cell(
        "from IPython.display import Image\n"
        "Image(filename = 'tree.png')"
    ),
]}
#start a new all_scripts[date] here

def write(date):
    '''Writes the scripts that were used in the given meeting date'''

    #error handling
    if date not in all_scripts.keys():
        raise ValueError(f'Date not found. Acceptable dates: {available_dates()}.')
    
    #notebook specification
    nb = all_scripts[date]['nb']

    #regular python files are NOT implemented yet; if they ever are, this can be the check
    if nb:
        for key in all_scripts[date].keys():
            
            if key == 'nb':
                continue

            notebook = nbf.v4.new_notebook()
            valid_cells = []
            for cell_content in all_scripts[date][key]:
                if isinstance(cell_content, str):
                    valid_cells.append(nbf.v4.new_code_cell(cell_content)) 
                else:
                    valid_cells.append(cell_content)  

            notebook.cells.extend(valid_cells)

            nbf.validate(notebook)  

            #writes file
            with open(all_scripts[date]['filename'], 'w') as f:
                nbf.write(notebook, f)

    else: # .py implementation
        pass 

def available_dates():
    return [key for key in all_scripts.keys()]

