import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
import torchvision.datasets as tv_datasets
from torch.utils.data import DataLoader, random_split
import threading
import time
import torch.nn.functional as F
import os
import moxing as mox  # 华为云ModelArts MOX组件

# OBS配置信息
OBS_CONFIG = {
    'obs_dir': 'obs://testmetadata/cifar-10-python',  # OBS数据集路径
    'local_dir': './data/cifar-10-batches-py'  # 本地临时路径，修改为实际数据存放路径
}


# 定义一个简单的卷积神经网络模型
class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 16 * 5 * 5)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)


# 从OBS下载CIFAR-10数据集
def download_cifar10_from_obs():
    """从OBS下载CIFAR-10数据集到本地"""
    local_dir = os.path.dirname(OBS_CONFIG['local_dir'])
    os.makedirs(local_dir, exist_ok=True)

    try:
        # 使用MOX从OBS复制数据集到本地
        print(f"正在从 {OBS_CONFIG['obs_dir']} 下载CIFAR-10数据集...")
        mox.file.copy_parallel(OBS_CONFIG['obs_dir'], local_dir)
        print("数据集下载完成")
        
        # 验证下载的文件
        validate_downloaded_data()
        
    except Exception as e:
        print(f"下载数据集时出错: {e}")
        print("尝试使用PyTorch自动下载...")
        download_via_torchvision()


# 验证下载的数据是否完整
def validate_downloaded_data():
    required_files = [
        'data_batch_1', 'data_batch_2', 'data_batch_3',
        'data_batch_4', 'data_batch_5', 'test_batch'
    ]
    
    for file in required_files:
        file_path = os.path.join(OBS_CONFIG['local_dir'], file)
        if not os.path.exists(file_path):
            raise RuntimeError(f"缺少必要的数据文件: {file}")


# 使用PyTorch内置功能下载数据集
def download_via_torchvision():
    """使用torchvision内置功能下载CIFAR-10数据集"""
    try:
        print("尝试使用torchvision自动下载...")
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        ])
        
        # 强制下载
        trainset = tv_datasets.CIFAR10(
            root='./data',
            train=True,
            download=True,
            transform=transform
        )
        
        testset = tv_datasets.CIFAR10(
            root='./data',
            train=False,
            download=True,
            transform=transform
        )
        
        print("使用torchvision下载成功")
        
    except Exception as e:
        print(f"自动下载失败: {e}")
        raise


# 数据加载函数
def load_data(partition_id: int, num_partitions: int):
    """加载CIFAR10分区数据"""
    # 确保数据集已下载且完整
    if not check_data_exists():
        download_cifar10_from_obs()

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])

    # 加载本地CIFAR10数据集，禁用自动下载
    trainset = tv_datasets.CIFAR10(
        root='./data',
        train=True,
        download=False,
        transform=transform
    )

    # 修复后的数据集分割逻辑
    partition_sizes = calculate_partition_sizes(len(trainset), num_partitions)
    partitions = random_split(trainset, partition_sizes)
    
    return DataLoader(partitions[partition_id], batch_size=4, shuffle=True)


# 计算正确的分区大小
def calculate_partition_sizes(total_size, num_partitions):
    """
    计算正确的分区大小，确保所有分区大小之和等于总大小
    """
    base_size = total_size // num_partitions
    remainder = total_size % num_partitions
    
    # 创建分区大小列表，前remainder个分区各多加1
    partition_sizes = [base_size + 1 if i < remainder else base_size for i in range(num_partitions)]
    
    # 验证总大小是否正确
    assert sum(partition_sizes) == total_size, "分区大小总和不等于数据集总大小"
    
    return partition_sizes


# 检查数据集是否存在且完整
def check_data_exists():
    """检查数据集是否存在且完整"""
    data_dir = os.path.dirname(OBS_CONFIG['local_dir'])
    batches_dir = os.path.basename(OBS_CONFIG['local_dir'])
    
    # 检查根目录和批次目录是否存在
    if not os.path.exists(data_dir) or not os.path.exists(OBS_CONFIG['local_dir']):
        return False
    
    # 检查必要的文件是否存在
    try:
        validate_downloaded_data()
        return True
    except RuntimeError:
        return False


# 定义损失函数和优化器
criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(SimpleCNN().parameters(), lr=0.001, momentum=0.9)


# 服务端类
class FederatedServer:
    def __init__(self, model, num_clients):
        self.model = model
        self.num_clients = num_clients
        self.client_updates = [None] * num_clients
        self.round = 0

    def aggregate_updates(self):
        # 聚合所有客户端的更新
        valid_updates = [update for update in self.client_updates if update is not None]
        if not valid_updates:
            print("没有有效的客户端更新")
            return

        for server_param in self.model.parameters():
            server_param.data.zero_()

        for client_update in valid_updates:
            for server_param, client_param in zip(self.model.parameters(), client_update.parameters()):
                server_param.data += client_param.data / len(valid_updates)

    def update_clients(self, clients):
        # 将模型参数分发给所有客户端
        for client in clients:
            client.model.load_state_dict(self.model.state_dict())

    def run(self):
        global clients  # 引用全局变量
        while self.round < 5:  # 运行5轮联邦学习
            print(f"Server: 开始第 {self.round + 1} 轮联邦学习")

            # 收集所有客户端的更新
            for i in range(self.num_clients):
                self.client_updates[i] = clients[i].train()

            # 聚合更新
            self.aggregate_updates()

            # 更新客户端模型
            self.update_clients(clients)

            self.round += 1
            time.sleep(1)  # 模拟每轮之间的延迟


# 客户端类
class FederatedClient:
    def __init__(self, model, partition_id, num_partitions):
        self.model = model
        self.partition_id = partition_id
        self.num_partitions = num_partitions
        self.dataloader = load_data(partition_id, num_partitions)

    def train(self):
        # 在本地数据上训练模型
        client_model = SimpleCNN()
        client_model.load_state_dict(self.model.state_dict())
        client_optimizer = optim.SGD(client_model.parameters(), lr=0.001, momentum=0.9)

        for epoch in range(1):  # 每轮训练1个epoch
            running_loss = 0.0
            for i, data in enumerate(self.dataloader, 0):
                inputs, labels = data

                client_optimizer.zero_grad()
                outputs = client_model(inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                client_optimizer.step()

                running_loss += loss.item()
                if i % 100 == 99:  # 每100个批次打印一次
                    print(
                        f"[客户端 {self.partition_id + 1}] 轮次: {epoch + 1}, 批次: {i + 1}, 损失: {running_loss / 100:.3f}")
                    running_loss = 0.0

        return client_model


# 初始化模型和服务端
global_model = SimpleCNN()
server = FederatedServer(global_model, 3)
clients = [FederatedClient(global_model, i, 3) for i in range(3)]

# 启动服务端线程
server_thread = threading.Thread(target=server.run)
server_thread.start()

# 启动客户端线程
client_threads = [threading.Thread(target=client.train) for client in clients]
for thread in client_threads:
    thread.start()

# 等待所有线程完成
server_thread.join()
for thread in client_threads:
    thread.join()